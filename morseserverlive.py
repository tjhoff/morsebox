import websockets
import asyncio
import threading
import time

class LiveServerMessageType:
    PULSE = 0
    MORSE = 1
    ASCII = 2

class LiveServer:
    def __init__(self):
        self.websocket_messages = {}
        self.messages_log = []
        self.messages_available = {}
        self.server_thread = None
        self.server_loop = None
        self.websocket_id = 0

    def send_message(self, client_id, channel_id, message_type, message_data):
        for websocket, messages in self.websocket_messages.items():
            messages.append([client_id, channel_id, message_type, message_data])
            # because asyncio is stupid "but there are no stupid programs, just stupid people!" YEAH WELL SHUT UP
            self.server_loop.call_soon_threadsafe(self.messages_available[websocket].set)

    def start(self):
        self.server_thread = threading.Thread(target=self._start_thread)
        self.server_thread.daemon = True
        self.server_thread.start()

    def _start_thread(self):
        self.server_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.server_loop)

        async def time(websocket, path):
            id = self.websocket_id
            self.websocket_id += 1
            self.websocket_messages[websocket] = []
            self.messages_available[websocket] = asyncio.Event()

            print("Websocket {0} connected - {0} total.".format(id, len(self.websocket_messages)))
            try:
                while True:
                    await self.messages_available[websocket].wait()
                    self.messages = self.websocket_messages[websocket]
                    for message in self.messages:
                        msg = "{0},{1},{2},{3}".format(message[0], message[1], message[2], message[3])
                        await websocket.send(msg)
                    self.messages_available[websocket].clear()
                    self.websocket_messages[websocket] = []
            finally:
                print("Websocket {0} disconnected".format(id))
                del self.websocket_messages[websocket]

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
