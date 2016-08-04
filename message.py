import struct

class MessageType:
    NONE = 0x00
    CLICK = 0x01
    HEARTBEAT = 0x02

    @staticmethod
    def to_bytes(type):
        return struct.pack("b", type)

def get_message(typebyte):
    message_type = struct.unpack("b", typebyte)[0]
    if message_type == ClickMessage.typebyte:
        return ClickMessage()

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
        data = struct.unpack(self.fmt, bytes)
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
