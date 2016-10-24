import message
import morseserver
import morseclient
import morseserverlive
import morsestream

import asyncio
import websockets
import threading
import time
import random

def test_live_websockets():
    ls = morseserverlive.LiveServer()
    ls.start()
    client_id = 1
    channel_id = 5
    type_id = 2
    data = "lol."

    time.sleep(.5)

    async def test_client():
        async with websockets.connect('ws://127.0.0.1:5678') as websocket:

            msg = await websocket.recv()
            msg_data = msg.split(",")
            assert int(msg_data[0])==client_id
            assert int(msg_data[1])==channel_id
            assert int(msg_data[2])==type_id
            assert msg_data[3] == data

    def run_client():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_until_complete(test_client())

    t = threading.Thread(target=run_client)
    t.start()

    ls.send_message(client_id, channel_id, type_id, data)

    t.join()

def test_live_integration():

    async def test_client():
        async with websockets.connect('ws://127.0.0.1:5678') as websocket:
            print("Websocket connected")
            msg = await websocket.recv()
            print("Websocket got {0}".format(msg))
            msg_data = msg.split(",")
            assert int(msg_data[0])==0
            assert int(msg_data[1])==0
            assert int(msg_data[2])==morseserverlive.LiveServerMessageType.PULSE
            assert msg_data[3].split(" ")[0] == "1"

    def run_client():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_until_complete(test_client())

    print("Initializing server")
    s = morseserver.Server("127.0.0.1", 5000)
    print("Initializing client")
    c = morseclient.MorseClient("127.0.0.1", 5000, 0, 0)

    c2 = morseclient.MorseClient("127.0.0.1", 5000, 1, 0)

    s.start()
    time.sleep(.1)

    t = threading.Thread(target=run_client)
    t.daemon = True
    #t.start()

    c.connect()
    c2.connect()

    time.sleep(.1)

    def run_client(client, message):
        while True:
            pulses = morsestream.MorseStream.generate_pulses(message, 4)
            for pulse in pulses:
                if not pulse[0]:
                    time.sleep(pulse[1])
                else:
                    client.press()
                    time.sleep(pulse[1])
                    client.unpress()
            client.unpress()

    t1 = threading.Thread(target=run_client, kwargs={"client": c, "message": "this is a test message"})

    t2 = threading.Thread(target=run_client, kwargs={"client": c2,  "message": "you're a test message!"})
    t1.daemon = t2.daemon = True
    t1.start()
    t2.start()

    t1.join()

    c.disconnect()
    c2.disconnect()
    s.close()


def test_message():
    msg = message.ClickMessage()
    msg.state = True
    msg.time = 1337.0
    msg_bytes = msg.to_bytes()
    assert len(msg_bytes) == msg.get_size() + 1

    msg2 = message.get_message(msg_bytes[0])
    msg2.from_bytes(msg_bytes[1:])
    assert msg2.state == msg.state
    assert msg2.time == msg.time

def test_server():
    print("Initializing server")
    s = morseserver.Server("127.0.0.1", 5000)
    print("Initializing client")
    c = morseclient.MorseClient("127.0.0.1", 5000, 0, 0)
    c2 = morseclient.MorseClient("127.0.0.1", 5000, 1, 0)

    c3 = morseclient.MorseClient("127.0.0.1", 5000, 2, 0)
    print("Starting server")
    s.start()
    print("Starting client")
    c.connect()
    time.sleep(.1)
    assert len(s.channels[0]) == 1
    c2.connect()
    time.sleep(.1)
    assert len(s.channels[0]) == 2
    time.sleep(.1)
    c3.connect()
    assert len(s.channels[0]) == 2

    print("Sending press")
    c.press()
    c.unpress()

    time.sleep(.1)

    c.disconnect()
    c2.disconnect()
    s.close()

if __name__ == "__main__":
    test_live_integration()
