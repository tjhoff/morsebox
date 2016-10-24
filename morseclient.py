#!/usr/bin/env python

import socket
import struct
import time
import threading
import logging
import select

from message import get_message, ClickMessage, HeartbeatMessage, RegisterMessage, MessageType

class MorseClient:

    BUFFER_SIZE = 20
    def __init__(self, ip, port, id, channel):
        self.s = None
        self.socklock = threading.Lock()
        self.ip = ip
        self.port = port
        self.connected = False
        self.id = id
        self.channel = channel

    def connect(self):
        connect_thread = threading.Thread(target=self._connect_thread)
        connect_thread.daemon = True
        connect_thread.start()

    def _connect_thread(self):
        while not self.connected:
            try:
                self.reconnect = False
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((self.ip, self.port))
                self.connected = True
                #self.s.settimeout(5)

                msg = RegisterMessage()
                msg.id = self.id
                msg.channel = self.channel

                try:
                    self.s.send(msg.to_bytes())
                except socket.error():
                    self.reconnect = True
                    self.disconnect()
                    continue

                self.on_connected()

                recv_thread = threading.Thread(target=self.recv)
                recv_thread.daemon = True
                recv_thread.start()
                recv_thread.join()
                if not self.reconnect:
                    break
                logging.info("Disconnected with reconnect set to true - retrying.")
            except socket.error as ex:
                logging.warn("Failed to connect.")
                time.sleep(.5)

    def disconnect(self):
        try:
            self.connected = False
            #self.s.shutdown(socket.SHUT_WR)
            self.s.close()
        except socket.error as ex:
            logging.exception("Got exception while trying to disconnect...")
            pass
        finally:
            self.on_disconnected()

    def _clickmsg(self, click):
        self.socklock.acquire()
        msg = ClickMessage()
        msg.state = click
        msg.time = time.time()
        try:
            self.s.send(msg.to_bytes())
        except socket.error as ex:
            logging.exception("Got socket error on send")
            self.reconnect = True
            self.disconnect()
        self.socklock.release()

    def press(self):
        self._clickmsg(True)

    def unpress(self):
        self._clickmsg(False)

    def recv(self):
        while self.connected:
            message = None
            try:
                data = self.s.recv(1)
                if data:
                    message = get_message(data)
                    if not message:
                        logging.warn("Message is of unknown type.")
                        continue
                    buf = bytearray()
                    while len(buf) < message.get_size():
                        buf += self.s.recv(min(self.BUFFER_SIZE, message.get_size() - len(buf)))
            except socket.error as ex:
                if socket.error == socket.timeout:
                    continue
                logging.exception("Got socket error on recv")
                self.reconnect = True
                self.disconnect()
                break
            if message:
                message.from_bytes(buf)

                if message.typebyte == MessageType.CLICK:
                    self.on_click_message(message.state)
        logging.info("Recv thread exiting")


    def on_click_message(self, click):
        logging.debug("Client got {0}".format(click))

    def on_connected(self):
        pass
    def on_disconnected(self):
        pass

if __name__ == "__main__":
    m = MorseClient()
    m.connect()
    time.sleep(.5)
    m.press()
    time.sleep(.5)
    m.unpress()
    time.sleep(50)
