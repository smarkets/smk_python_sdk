import errno
import logging
import socket

from smk.exceptions import ConnectionError
from smk.seto_pb2 import payload


class Session(object):
    "Manages TCP communication via Smarkets streaming API"
    logger = logging.getLogger('smk.session')
    def __init__(self, username, password, host='localhost', port=3701,
                 session=None, inseq=1, outseq=1, socket_timeout=None):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.session = session
        self.inseq = inseq
        self.outseq = outseq
        self.socket_timeout = socket_timeout
        self._buffer = ''
        self._sock = None

    def connect(self):
        "Connects to the API if not already connected"
        if self._sock is not None:
            self.logger.debug("connect() called, but already connected")
            return
        try:
            sock = self._connect()
        except socket.error as e:
            raise ConnectionError(self._error_message(e))

        self._sock = sock
        self.on_connect()

    def _connect(self):
        "Create a TCP socket connection"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.socket_timeout)
        self.logger.info(
            "connecting with new socket to %s:%s", self.host, self.port)
        sock.connect((self.host, self.port))
        return sock

    def _error_message(self, exception):
        # args for socket.error can either be (errno, "message")
        # or just "message"
        if len(exception.args) == 1:
            return "Error connecting to %s:%s. %s." % (
                self.host, self.port, exception.args[0])
        else:
            return "Error %s connecting %s:%s. %s." % (
                exception.args[0], self.host, self.port,
                exception.args[1])

    def on_connect(self):
        "Initialise the connection by logging in"
        login_payload = payload()
        login_payload.sequenced.message_data.login.username = self.username
        login_payload.sequenced.message_data.login.password = self.password
        self.logger.info("sending login payload")
        if self.session is not None:
            self.logger.info("attempting to resume session %s", self.session)
            login_payload.sequenced.message_data.login.session = self.session
        self.send_payload(login_payload)

    def disconnect(self):
        "Disconnect from the API"
        if self._sock is None:
            self.logger.debug("disconnect() called with no socket, ignoring")
            return
        try:
            self.logger.info("closing socket")
            self._sock.close()
        except socket.error:
            # Ignore exceptions while disconnecting
            pass
        self._sock = None

    def send_frame(self, frame):
        "Send a framed message to the service"
        if not self._sock:
            self.logger.warning(
                "send_frame called while disconnected. connecting...")
            self.connect()
        try:
            self.logger.debug("sending frame bytes %s", frame)
            self._sock.sendall(frame)
        except socket.error as e:
            # Die fast
            self.disconnect()
            if len(e.args) == 1:
                _errno, errmsg = 'UNKNOWN', e.args[0]
            else:
                _errno, errmsg = e.args
            raise ConnectionError("Error %s while writing to socket. %s." % (
                    _errno, errmsg))
        except:
            # Try to disconnect anyway
            self.disconnect()
            raise

    def send_payload(self, payload_out):
        "Serialise, sequence, add header, and send payload"
        self.logger.debug(
            "sending payload with outgoing sequence %d", self.outseq)
        payload_out.sequenced.seq = self.outseq
        msg_bytes = payload_out.SerializeToString()
        byte_count = len(msg_bytes)
        # Pad to 4 bytes
        padding = '\x00' * max(0, 3 - byte_count)
        self.logger.debug(
            "payload has %d bytes and needs %d padding",
            byte_count, len(padding))
        frame = _encode_varint(byte_count) + msg_bytes + padding
        self.send_frame(frame)
        self.outseq += 1

    def read_frame(self):
        "Read a frame with header"
        msg = payload()
        # Read a minimum of 4 bytes
        bytes_needed = 4 - len(self._buffer)
        if bytes_needed:
            self.logger.debug("receiving %d bytes", bytes_needed)
            self._buffer += self._sock.recv(bytes_needed, socket.MSG_WAITALL)
        result = 0
        shift = 0
        pos = 0
        while 1:
            if pos > len(self._buffer) - 1:
                pos = 0
                # Empty buffer and read another 4 bytes
                self._buffer = self._sock.recv(4, socket.MSG_WAITALL)
            b = ord(self._buffer[pos])
            result |= ((b & 0x7f) << shift)
            pos += 1
            if not (b & 0x80):
                self._buffer = self._buffer[pos:]
                to_read = max(0, result - len(self._buffer))
                self.logger.debug("next message is %d bytes long", to_read)
                if to_read:
                    # Read the actual message if necessary
                    self._buffer += self._sock.recv(to_read, socket.MSG_WAITALL)
                msg_bytes = self._buffer[:result]
                self.logger.debug("parsing bytes %s", msg_bytes)
                msg.ParseFromString(msg_bytes)
                # Consume the buffer
                self._buffer = self._buffer[result:]
                return self._handle_login_response(msg)
            shift += 7

    def next_frame(self):
        "Get the next frame and increment inseq"
        payload_in = self.read_frame()
        if payload_in.sequenced.seq == self.inseq:
            # Go ahead
            self.logger.debug("received sequence %d", self.inseq)
            return payload_in
        elif payload_in.sequenced.message_data.replay.seq:
            # Just a replay message, sequence not important
            seq = payload_in.sequenced.message_data.replay.seq
            self.logger.debug("received a replay message with sequence %d", seq)
            return None
        elif payload_in.sequenced.seq > self.inseq:
            # Need a replay
            self.logger.debug(
                "received incoming sequence %d, expected %d",
                payload_in.sequenced.seq,
                self.inseq)
            replay = payload()
            replay.sequenced.message_data.replay.seq = self.inseq
            self.send_payload(replay)
            return None
        else:
            return None

    def _handle_login_response(self, msg):
        "Pre-consume the login response message"
        if msg.sequenced.message_data.login_response.session:
            self.session = msg.sequenced.message_data.login_response.session
            self.outseq = msg.sequenced.message_data.login_response.reset
            self.logger.info(
                "received login_response with session %s and reset %d",
                self.session,
                self.outseq)
        return msg


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
