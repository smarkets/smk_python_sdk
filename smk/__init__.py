import socket
import seto_pb2
import struct
from Queue import Queue
from threading import Thread


__version__ = '0.1.0'
__all__ = ['DecodeError', 'Client']


VERSION = tuple(map(int, __version__.split('.')))


class DecodeError(Exception):
    "Error encountered decoding a frame"
    pass


class Client(Thread):

    class Out(Thread):
        def __init__(self, sock, seq=1):
            self.sock = sock
            self.seq = seq
            self.q = Queue(0)
            Thread.__init__(self)

        def send(self, msg):
            self.q.put(msg)
            # todo: for persistence this should also log to a file
            # that means we need 2 threads here, one for allocating
            # sequence numbers and logging to file, the other as the
            # sender thread

        def run(self):
            while True:
                msg = None
                msg_bytes = None
                byte_count = None
                header = None

                msg = self.q.get(True)
                msg.sequenced.seq = self.seq
                msg_bytes = msg.SerializeToString()
                byte_count = len(msg_bytes)
                # Pad to 4 bytes
                padding = '\x00' * max(0, 3 - byte_count)
                frame = _encode_varint(byte_count) + msg_bytes + padding
                self.sock.send(frame)
                self.q.task_done()
                self.seq += 1

    def __init__(self):
        Thread.__init__(self)

    def order(self, qty, price, side, group, contract):
        msg = seto_pb2.payload()
        msg.sequenced.message_data.order_create.quantity = qty
        msg.sequenced.message_data.order_create.price = price
        msg.sequenced.message_data.order_create.side = side
        msg.sequenced.message_data.order_create.group = group
        msg.sequenced.message_data.order_create.contract = contract
        self.out.send(msg)

    def order_cancel(self, order):
        msg = seto_pb2.payload()
        msg.sequenced.message_data.order_cancel.order = order
        self.out.send(msg)

    def ping(self):
        msg = seto_pb2.payload()
        msg.sequenced.message_data.ping = True
        self.out.send(msg)

    def subscribe(self, group):
        msg = seto_pb2.payload()
        msg.sequenced.message_data.market_subscription.group = group
        self.out.send(msg)

    def unsubscribe(self, group):
        msg = seto_pb2.payload()
        msg.message.market_unsubscription.group = group
        self.out.send(msg)

    def login(self, host, port, username, password, session=None, inseq=1, outseq=1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        self.out = Client.Out(sock, outseq)
        self.out.start()
        self.inseq = inseq
        msg = seto_pb2.payload()
        msg.sequenced.message_data.login.username = username
        msg.sequenced.message_data.login.password = password
        if session:
            msg.sequenced.message_data.login.session = session
        self.out.send(msg)
        self.sock = sock
        self.buffer = ''
        self.start()

    def _read_frame(self):
        """
        Read a frame with header
        """
        msg = seto_pb2.payload()
        # Read a minimum of 4 bytes
        bytes_needed = 4 - len(self.buffer)
        if bytes_needed:
            self.buffer += self.sock.recv(bytes_needed, socket.MSG_WAITALL)
        result = 0
        shift = 0
        pos = 0
        while 1:
            if pos > len(self.buffer) - 1:
                pos = 0
                # Empty buffer and read another 4 bytes
                self.buffer = self.sock.recv(4, socket.MSG_WAITALL)
            b = ord(self.buffer[pos])
            result |= ((b & 0x7f) << shift)
            pos += 1
            if not (b & 0x80):
                self.buffer = self.buffer[pos:]
                to_read = max(0, result - len(self.buffer))
                if to_read:
                    # Read the actual message if necessary
                    self.buffer += self.sock.recv(to_read, socket.MSG_WAITALL)
                msg.ParseFromString(self.buffer[:result])
                # Consume the buffer
                self.buffer = self.buffer[result:]
                return msg
            shift += 7

    def run(self):
        while True:
            msg = self._read_frame()
            if self.pre_handle(msg):
                try:
                    self.handle(msg)
                    self.inseq += 1
                except Exception, e:
                    print "Error handling message", msg, e

    def pre_handle(self, msg):
        if msg.sequenced.seq == self.inseq:
            return True # correct sequence
        elif msg.sequenced.message_data.replay.seq:
            # replay message, sequence not important, process it here
            return False
        elif msg.sequenced.seq > self.inseq:
            replay = seto_pb2.payload()
            replay.sequenced.message_data.replay.seq = self.inseq
            self.out.send(replay)
            return False
        else:
            return False

    def handle(self, msg):
        if msg.sequenced.message_data.login_response.session:
            self.session = msg.sequenced.message_data.login_response.session
            self.out.seq = msg.sequenced.message_data.login_response.reset
            print "Session", msg.sequenced.message_data.login_response.session
        elif msg.sequenced.message_data.order_accepted.order:
            print "Order Accepted", msg.sequenced.message_data.order_accepted.seq, msg.sequenced.message_data.order_accepted.order
        elif msg.sequenced.message_data.order_executed.order:
            print "Order Executed", msg.sequenced.message_data.order_executed.order, \
                    msg.sequenced.message_data.order_executed.price,\
                    msg.sequenced.message_data.order_executed.quantity
        elif msg.sequenced.message_data.order_cancelled.order:
            print "Order Cancelled", msg.sequenced.message_data.order_cancelled.order, msg.sequenced.message_data.order_cancelled.reason
        elif msg.sequenced.message_data.pong:
            print "Pong"
        elif msg.sequenced.message_data.market_quotes:
            print "Quotes ", msg.sequenced.message_data.market_quotes.group


def _encode_varint(value):
    """
    Encode an int/long as a ULEB128 number
    """
    bits = value & 0x7f
    value >>= 7
    ret = ''
    while value:
        ret += chr(0x80|bits)
        bits = value & 0x7f
        value >>= 7
    return ret + chr(bits)
