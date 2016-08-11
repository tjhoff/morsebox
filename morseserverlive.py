import websockets
import asyncio
import threading
import time

class LiveServer:
    def __init__(self):
        self.messages = []
        self.messages_available = threading.Event()
        self.server_thread = None

    def on_message(self, client_id, channel_id, message_type, message_data):

        self.messages.append([client_id, channel_id, message_type, message_data])
        self.messages_available.set()

    def start(self):
        self.server_thread = threading.Thread(target=self._start_thread)
        self.server_thread.daemon = True
        self.server_thread.start()

    def _start_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def time(websocket, path):
            while True:
                self.messages_available.wait()
                self.messages_available.clear()
                for message in self.messages:
                    msg = "{0},{1},{2},{3}".format(message[0], message[1], message[2], message[3])
                    await websocket.send(msg)
                self.messages = []

        start_server = websockets.serve(time, '127.0.0.1', 5678)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    ls = LiveServer()
    ls.start()
    msgid = 0
    while True:
        msgid += 1
        ls.on_message(0,0,0, "hi{0}!".format(msgid))
        time.sleep(.5)
