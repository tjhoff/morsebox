#!/usr/bin/env python

import socket
import struct
import time
import threading

TCP_IP = 'gentlemeninventors.com'
TCP_PORT = 5005
BUFFER_SIZE = 20
MESSAGE = "Hello, World!"

class MorseClient:
    def __init__(self):
        self.s = None

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.s.connect((TCP_IP, TCP_PORT))
                break
            except socket.error:
                time.sleep(.5)
        recv_thread = threading.Thread(target=self.recv)
        recv_thread.daemon = True
        recv_thread.start()

    def press(self):
        self.s.send(struct.pack("?d", True, time.time()))

    def unpress(self):
        self.s.send(struct.pack("?d", False, time.time()))

    def recv(self):
        while 1:
            data = self.s.recv(BUFFER_SIZE)
            if data:
                self.on_data(data)

    def on_data(self, data):
        d = struct.unpack("?d", data)
        if d[0]:
            print "on at {0}".format(d[1])
        else:
            print "off at {0}".format(d[1])

if __name__ == "__main__":
    m = MorseClient()
    m.connect()
    time.sleep(.5)
    m.press()
    time.sleep(.5)
    m.unpress()
    time.sleep(50)
