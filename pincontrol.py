
import time
import struct
import RPi.GPIO as GPIO
from morseclient import MorseClient

BUTTON_CHANNEL = 2
BUTTON_LED_CHANNEL = 3
LED_CHANNEL = 4

class BoxMorseClient(MorseClient):
    def __init__(self):
        MorseClient.__init__(self)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(3, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(4, GPIO.OUT, initial=GPIO.LOW)
        self.last_state = False

    def connect(self):
        MorseClient.connect(self)

    def press(self):
        MorseClient.press(self)
        self.setButtonLed(0)

    def unpress(self):
        MorseClient.unpress(self)
        self.setButtonLed(1)

    def on_data(self, data):

        #deal with timing here.
        d = struct.unpack("?d", data)
        state = d[0]
        time = d[1]

        self.setLed(state == True)

    def checkButton(self):
        return GPIO.input(14)

    def setButtonLed(self, state):
        GPIO.output(3, state)

    def setLed(self, state):
        print "LED is {0}".format(state)
        GPIO.output(4, state)

if __name__ == "__main__":
    mc = BoxMorseClient()
    mc.connect()

    while 1:
        time.sleep(.01)
        button_state = mc.checkButton()
        if button_state != mc.last_state:
            if button_state:
                mc.press()
            else:
                mc.unpress()
            mc.last_state = button_state
