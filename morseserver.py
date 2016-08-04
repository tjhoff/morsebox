#!/usr/bin/env python

import socket
import struct
import threading
import time

from morsestream import MorseStream

TCP_IP = '0.0.0.0'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))

s.listen(1)

clients = []

class Client:
    next_id = 0
    def __init__(self, conn, addr, on_data, on_closed):
        self.conn = conn
        self.addr = addr
        self.conn_thread = None
        self.ms = None
        self.data_callback = on_data
        self.closed_callback = on_closed
        self.open = False
        self.id = self.next_id
        self.next_id += 1

    def start(self):
        self.open = True
        self.conn_thread = threading.Thread(target=self._recvthread)
        self.conn_thread.daemon = True
        self.conn_thread.start()

    def _recvthread(self):
        last_signal = time.time()
        self.ms = MorseStream()
        data = ""
        while self.open:

            try:

                while (not data or len(data) < 16):
                    data += self.conn.recv(BUFFER_SIZE)
            except socket.error:
                # better error handling here plox
                print "Socket encountered error"
                self.open = False
                break
            d = struct.unpack("?d", data[:16])
            data = data[16:]

            self.ms.add_pulse(not d[0], time.time() - last_signal)
            last_signal = time.time()

            self.data_callback(self, d)

        self.close()

    def close(self):
        self.conn.close()
        self.closed_callback(self)

    def send_data(self, data):
        try:
            self.conn.send_data(data)
        except socket.error:
            print "Socket encountered error on send data"
            self.close()

def on_closed(client):
    clients.remove(client)
    print("Client {0} disconnected".format(client.id))

def on_data(client, data):
    print("Data {0} from client {1}".format(data, client.id))
    if d:
        for client in clients:
            if (client == conn):
                continue

try:
    while True:

        conn, addr = s.accept()
        print dir(conn)

        client = Client(conn, addr, on_data, on_closed)
        print("New client connected - id {0}".format(client.id))
        client.start()

        clients.append(client)
except Exception as ex:
    print(ex)
    for client in clients:
        client.close()
finally:
    s.close()
