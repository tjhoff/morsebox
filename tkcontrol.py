from Tkinter import *
from morseclient import MorseClient
import time

class TkMorseClient(MorseClient):
    def __init__(self):
        MorseClient.__init__(self)

    def onData(self, data):
        d = struct.unpack("?d", data)
        if d[0]:
            print "on at {0}".format(d[1])
        else:
            print "off at {0}".format(d[1])

if __name__ == "__main__":
    mc = TkMorseClient()
    mc.connect()
    pressed = False
    last_event = time.clock()

    def keyup(e):
        global pressed, last_event
        if e.char == 'b':
            pass

    def keydown(e):
        global pressed, last_event
        if e.char == 'b':
            mc.press()
        if e.char == 'n':
            mc.unpress()

    root = Tk()
    frame = Frame(root, width=100, height=100)
    frame.bind("<KeyPress>", keydown)
    frame.bind("<KeyRelease>", keyup)
    frame.pack()
    frame.focus_set()
    root.mainloop()
