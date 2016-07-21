#!/usr/bin/env python

import socket
import struct
import threading

TCP_IP = '0.0.0.0'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))

s.listen(1)

connections = []

def recv(conn, addr):
    while 1:
        try:

            data = conn.recv(BUFFER_SIZE)
        except socket.error:
            # better error handling here plox
            print "Socket encountered error"
            break
        if not data: break
        d = struct.unpack("?d", data)
        if d:
            for connection in connections:
                if (conn == connection):
                    print "skipping self"
                    continue
                try:
                    connection.send(data)
                except socket.error:
                    print "Failed sending data to connection"

    conn.close()

try:

    while True:

        conn, addr = s.accept()
        print dir(conn)

        print 'Connection address:', addr

        conn_thread = threading.Thread(target=recv, args=[conn, addr])
        conn_thread.daemon = True
        conn_thread.start()

        connections.append(conn)
except KeyboardInterrupt:
    for connection in connections:
        connection.close()
