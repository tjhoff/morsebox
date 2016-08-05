
import time
import struct
import RPi.GPIO as GPIO
from morseclient import MorseClient

BUTTON = 14
BUTTON_LED = 15
BLUE_LED = 18

class BoxMorseClient(MorseClient):
    def __init__(self, ip, port, id, channel):
        MorseClient.__init__(self, ip, port, id, channel)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUTTON_LED, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(BLUE_LED, GPIO.OUT, initial=GPIO.LOW)
        self.last_state = False

    def connect(self):
        MorseClient.connect(self)

    def error(self, flashes = 4):
        for i in range(flashes):
            self.setButtonLed(1)
            time.sleep(.1)
            self.setButtonLed(0)
            time.sleep(.1)

    def press(self):
        if self.connected:
            MorseClient.press(self)
            self.setButtonLed(0)

    def unpress(self):
        if self.connected:
            MorseClient.unpress(self)
            self.setButtonLed(1)
        else:
            self.error()

    def on_connected(self):
        self.setButtonLed(1)

    def on_disconnected(self):
        self.setButtonLed(0)

    def on_click_message(self, click):
        self.setLed(click)

    def checkButton(self):
        return not GPIO.input(BUTTON)

    def setButtonLed(self, state):
        GPIO.output(BUTTON_LED, state)

    def setLed(self, state):
        print "LED is {0}".format(state)
        GPIO.output(BLUE_LED, state)

if __name__ == "__main__":
    import json

    with open("client_config.json") as f:
        config = f.read()

    json_config = json.loads(config)

    server = json_config["server"]
    port = int(json_config["port"])
    id = int(json_config["id"])
    channel = int(json_config["channel"])

    mc = BoxMorseClient(server, port, id, channel)
    mc.connect()
    pulses = []
    last_state_time = time.time()
    try:
        while 1:
            time.sleep(.01)
            button_state = mc.checkButton()
            if button_state != mc.last_state:
                if button_state:
                    length = time.time() - last_state_time
                    last_state_time = time.time()
                    pulses.append((False, length))
                    mc.press()
                else:
                    length = time.time() - last_state_time
                    last_state_time = time.time()
                    pulses.append((True, length))
                    mc.unpress()
                mc.last_state = button_state
    except KeyboardInterrupt:
        print pulses
