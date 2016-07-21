from morseclient import MorseClient

class CliMorseClient(MorseClient):
    def __init__(self):
        MorseClient.__init__(self)

    def onData(self, data):
        d = struct.unpack("?d", data)
        if d[0]:
            print "on at {0}".format(d[1])
        else:
            print "off at {0}".format(d[1])

if __name__ == "__main__":
    mc = CliMorseClient()
    mc.connect()

    input = None
    while input != "exit":
        input = raw_input()
        if input == "on":
            mc.press()
        elif input == "off":
            mc.unpress()
