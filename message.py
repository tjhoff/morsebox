import struct

class MessageType:
    NONE = 0x00
    CLICK = 0x01
    HEARTBEAT = 0x02
    REGISTER = 0x03

    @staticmethod
    def to_bytes(type):
        return struct.pack("b", type)

def get_message(typebyte):
    print(typebyte)
    try:
        message_type = struct.unpack("b", typebyte)[0]
    except TypeError:
        message_type = typebyte
    if message_type == ClickMessage.typebyte:
        return ClickMessage()
    if message_type == RegisterMessage.typebyte:
        return RegisterMessage()
    if message_type == HeartbeatMessage.typebyte:
        return HeartbeatMessage()
    return None

class Message:
    typebyte = MessageType.NONE
    def __init__(self):
        self.fmt = ""

    def to_bytes(self):
        return ""

    def from_bytes(self, bytes):
        pass

    def get_size(self):
        return struct.calcsize(self.fmt)

class ClickMessage(Message):
    typebyte = MessageType.CLICK
    def __init__(self):
        self.fmt = "?d"
        self.state = None
        self.time = None

    def to_bytes(self):
        return MessageType.to_bytes(self.typebyte) + struct.pack(self.fmt, self.state, self.time)

    def from_bytes(self, bytes):
        data = None
        try:
            data = struct.unpack(self.fmt, bytes)
        except:
            print("Bytes is {0} and {1}".format(len(bytes), bytes))
            return
        self.state = data[0]
        self.time = data[1]

class HeartbeatMessage(Message):
    typebyte =MessageType.HEARTBEAT
    def __init__(self):
        self.fmt = "i"
        self.id = None

    def to_bytes(self):
        return MessageType.to_bytes(self.typebyte) + struct.pack(self.fmt, self.id)

    def from_bytes(self, bytes):
        data = struct.unpack(self.fmt, bytes)
        self.id = data[0]

class RegisterMessage(Message):
    typebyte = MessageType.REGISTER
    def __init__(self):
        self.fmt = "ii"
        self.id = None
        self.channel = None

    def to_bytes(self):
        return MessageType.to_bytes(self.typebyte) + struct.pack(self.fmt, self.id, self.channel)

    def from_bytes(self, bytes):
        data = struct.unpack(self.fmt, bytes)
        self.id = data[0]
        self.channel = data[1]
