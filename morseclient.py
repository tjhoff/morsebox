#!/usr/bin/env python

import socket
import struct
import time
import threading

from message import get_message, ClickMessage, HeartbeatMessage, MessageType

TCP_IP = 'gentlemeninventors.com'
TCP_PORT = 5005
BUFFER_SIZE = 20
MESSAGE = "Hello, World!"

class MorseClient:
    def __init__(self):
        self.s = None
        self.socklock = threading.Lock()

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

    def _clickmsg(self, click):
        self.socklock.acquire()
        msg = ClickMessage()
        msg.click = click
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
                    buf = ""
                    while buf < message.get_size():
                        buf += self.s.recv(min(BUFFER_SIZE, len(message.get_size() - buf)))
            except socket.error as ex:
                print "Got socket error on recv - {0}".format(ex)
            finally:
                pass

            if (message):
                message.from_bytes(buf)

                if message.typebyte == MessageType.ClickMessage:
                    self.on_click_message(message.click)

    def on_click_message(self, click):
        pass

if __name__ == "__main__":
    m = MorseClient()
    m.connect()
    time.sleep(.5)
    m.press()
    time.sleep(.5)
    m.unpress()
    time.sleep(50)
