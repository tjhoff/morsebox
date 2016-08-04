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

connections = []

class Connection:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.conn_thread = None
        self.ms = None

    def start(self):
        self.conn_thread = threading.Thread(target=self._recvthread)
        self.conn_thread.daemon = True
        self.conn_thread.start()

    def _recvthread(self):
        last_signal = time.time()
        self.ms = MorseStream()
        while 1:
            try:
                data = ""
                while (not data or len(data) < 16):

                    data += self.conn.recv(BUFFER_SIZE)
            except socket.error:
                # better error handling here plox
                print "Socket encountered error"
                break
            d = struct.unpack("?d", data)

            self.ms.add_pulse(not d[0], time.time() - last_signal)
            last_signal = time.time()

            if d:
                for connection in connections:
                    if (conn == connection):
                        continue
                    try:
                        connection.send(data)
                    except socket.error:
                        print "Failed sending data to connection"

        self.conn.close()

def on_closed(conn):

def on_data(conn, data):
    for connection in connections:


try:

    while True:

        conn, addr = s.accept()
        print dir(conn)

        print 'Connection address:', addr



        connections.append(conn)
except KeyboardInterrupt:
    for connection in connections:
        connection.close()
    s.close()
