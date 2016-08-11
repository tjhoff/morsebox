#!/usr/bin/env python

import socket
import struct
import threading
import time
import json

from morsestream import MorseStream
from morsewebserverlive import LiveClient
from message import get_message, ClickMessage, HeartbeatMessage, MessageType

class Server:

    def __init__(self, ip, port):

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((ip, port))

        self.s.listen(3)

        self.clients = []
        self.channels = {}
        self.running = True

    def start(self):

        self.start_thread = threading.Thread(target=self._run_server)
        self.start_thread.daemon = True
        self.start_thread.start()

    def _run_server(self):
        try:
            while True:
                print("Waiting for connection")
                conn, addr = self.s.accept()

                client = Client(conn, addr, self.on_message, self.on_closed)
                print("New client connected - id {0}".format(client.id))
                client.start()

                self.clients.append(client)
        except Exception as ex:
            print(ex)
            for client in self.clients:
                client.close()
        finally:
            self.s.close()

    def close(self):
        self.s.close()

    def on_closed(self, client):
        self.clients.remove(client)
        if client.channel and client.channel in self.channels and client in self.channels[client.channel]:
            self.channels[client.channel].remove(client)
            print("Client {0} removed from channel {1}".format(client.id, client.channel))
        print("Client {0} disconnected".format(client.id))

    def on_message(self, client, msg):
        print("Data {0} from client {1}".format(msg, client.id))
        if not msg:
            return

        if msg.typebyte == MessageType.REGISTER:
            channel = msg.channel

            if channel not in self.channels:
                print "Created channel {0}".format(channel)
                self.channels[channel] = []
            print("Adding {0} to {1}".format(client.id, channel))
            if len(self.channels[channel]) < 2:
                self.channels[channel].append(client)
                client.id = msg.id
                client.channel = channel
            else:
                print "Request to join full channel {0} from {1}".format(channel, client.addr)
                client.close()

        elif msg.typebyte == MessageType.CLICK:
            if not client.channel:
                return

            for c in self.channels[client.channel]:
                if c.id == client.id:
                    continue
                c.send_message(msg)

        elif msg.typebyte == MessageType.HEARTBEAT:
            pass


class Client:
    BUFFER_SIZE = 20  # Normally 1024, but we want fast response

    def __init__(self, conn, addr, on_message, on_closed):
        self.conn = conn
        self.addr = addr
        self.conn_thread = None
        self.ms = None
        self.message_callback = on_message
        self.closed_callback = on_closed
        self.open = False
        self.socklock = threading.Lock()
        self.id = None
        self.channel = None

    def start(self):
        self.open = True
        self.conn_thread = threading.Thread(target=self._recvthread)
        self.conn_thread.daemon = True
        self.conn_thread.start()

    def _recvthread(self):
        last_signal = time.time()
        self.ms = MorseStream()
        while self.open:
            try:
                data = self.conn.recv(1)
                if data:
                    message = get_message(data)
                    buf = ""
                    while len(buf) < message.get_size():
                        buf += self.conn.recv(min(self.BUFFER_SIZE, message.get_size() - len(buf)))

                    message.from_bytes(buf)

                    self.message_callback(self, message)
            except socket.error:
                # better error handling here plox
                print "Socket encountered error"
                self.open = False
                break

            #self.ms.add_pulse(not d[0], time.time() - last_signal)
            last_signal = time.time()

        self.close()

    def close(self):
        try:
            self.conn.close()
        except socket.error:
            print "Error on closing {0}".format(self.id)
        self.closed_callback(self)

    def send_message(self, message):
        try:
            self.socklock.acquire()
            self.conn.send(message.to_bytes())
            self.socklock.release()
        except socket.error:
            print "Socket encountered error on send data"
            self.close()

if __name__ == "__main__":
    s = None

    import json

    with open("server_config.json") as f:
        config = f.read()

    json_config = json.loads(config)

    ip = json_config["ip"]
    port = int(json_config["port"])

    try:
        s = Server(ip, port)
        s.start()
        while s.start_thread.is_alive:
            s.start_thread.join(5)
    except Exception as ex:
        print("Encountered exception in main thread: {0}".format(ex))
    finally:
        s.close()
