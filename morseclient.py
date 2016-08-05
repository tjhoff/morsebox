#!/usr/bin/env python

import socket
import struct
import time
import threading

from message import get_message, ClickMessage, HeartbeatMessage, MessageType

TCP_IP = 'gentlemeninventors.com'
TCP_PORT = 5005

class MorseClient:

    BUFFER_SIZE = 20
    def __init__(self, ip, port):
        self.s = None
        self.socklock = threading.Lock()
        self.ip = ip
        self.port = port

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.s.connect((self.ip, self.port))
                break
            except socket.error as ex:
                print "Failed to connect - {0}".format(ex)
                time.sleep(.5)
        recv_thread = threading.Thread(target=self.recv)
        recv_thread.daemon = True
        recv_thread.start()

    def disconnect(self):
        self.s.close()

    def _clickmsg(self, click):
        self.socklock.acquire()
        msg = ClickMessage()
        msg.state = click
        msg.time = time.time()

        self.s.send(msg.to_bytes())
        self.socklock.release()

    def press(self):
        self._clickmsg(True)

    def unpress(self):
        self._clickmsg(False)

    def recv(self):
        while 1:

            message = None
            try:
                data = self.s.recv(1)
                if data:
                    message = get_message(data)
                    if not message:
                        print "Message is of unknown type."
                        continue
                    buf = ""
                    while len(buf) < message.get_size():
                        buf += self.s.recv(min(self.BUFFER_SIZE, message.get_size() - len(buf)))
            except socket.error as ex:
                print "Got socket error on recv - {0}".format(ex)
            finally:
                pass

            if message:
                message.from_bytes(buf)
                print message.state
                print message.time

                if message.typebyte == MessageType.CLICK:
                    self.on_click_message(message.state)

    def on_click_message(self, click):
        print "Client got {0}".format(click)

if __name__ == "__main__":
    m = MorseClient()
    m.connect()
    time.sleep(.5)
    m.press()
    time.sleep(.5)
    m.unpress()
    time.sleep(50)
