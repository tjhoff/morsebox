import message
import morseserver
import morseclient
import morseserverlive

import asyncio
import websockets
import time

def test_live_websockets():
    ls = morseserverlive.LiveServer()
    ls.start()
    client_id = 1
    channel_id = 5
    type_id = 2
    data = "lol."

    ls.on_message(client_id, channel_id, type_id, data)

    async def test_client():
        async with websockets.connect('ws://localhost:8765') as websocket:

            msg = await websocket.recv()
            msg_data = msg.split(",")
            assert int(msg_data[0])==client_id
            assert int(msg_data[1])==channel_id
            assert int(msg_data[2])==type_id
            assert msg_data[3] == data

    asyncio.get_event_loop().run_until_complete(test_client())


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
    test_server()
