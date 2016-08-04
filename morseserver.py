#!/usr/bin/env python

import socket
import struct
import threading
import time

from morsestream import MorseStream
from message import get_message, ClickMessage, HeartbeatMessage

TCP_IP = '0.0.0.0'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))

s.listen(1)

clients = []

class Client:
    next_id = 0
    def __init__(self, conn, addr, on_message, on_closed):
        self.conn = conn
        self.addr = addr
        self.conn_thread = None
        self.ms = None
        self.message_callback = on_message
        self.closed_callback = on_closed
        self.open = False
        self.socklock = threading.Lock()
        self.id = self.next_id
        Client.next_id += 1

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
                        buf += self.conn.recv(min(BUFFER_SIZE, message.get_size() - len(buf)))

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
            self.sockock.acquire()
            self.conn.send(message.to_bytes())
            self.socklock.release()
        except socket.error:
            print "Socket encountered error on send data"
            self.close()

def on_closed(client):
    clients.remove(client)
    print("Client {0} disconnected".format(client.id))

def on_message(client, msg):
    print("Data {0} from client {1}".format(msg, client.id))

    if msg:
        for c in clients:
            if (c.id == client.id):
                continue
            c.send_message(msg)

try:
    while True:

        conn, addr = s.accept()
        print dir(conn)

        client = Client(conn, addr, on_message, on_closed)
        print("New client connected - id {0}".format(client.id))
        client.start()

        clients.append(client)
except Exception as ex:
    print(ex)
    for client in clients:
        client.close()
finally:
    s.close()
