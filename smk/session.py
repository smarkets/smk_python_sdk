"Smarkets TCP-based session management"
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
        self.in_payload = payload()
        self.out_payload = payload()

    def connect(self):
        "Connects to the API if not already connected"
        if self._sock is not None:
            self.logger.debug("connect() called, but already connected")
            return
        try:
            sock = self._connect()
        except socket.error as exc:
            raise ConnectionError(self._error_message(exc))

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
        "Stringify a socket exception"
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
        login_payload = self.out_payload
        login_payload.Clear()
        # pylint: disable-msg=E1101
        login_payload.sequenced.message_data.login.username = self.username
        login_payload.sequenced.message_data.login.password = self.password
        self.logger.info("sending login payload")
        if self.session is not None:
            self.logger.info("attempting to resume session %s", self.session)
            login_payload.sequenced.message_data.login.session = self.session
        self.send_payload()

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
            self.logger.debug("sending frame bytes %r", frame)
            self._sock.sendall(frame)
        except socket.error as exc:
            # Die fast
            self.disconnect()
            if len(exc.args) == 1:
                _errno, errmsg = 'UNKNOWN', exc.args[0]
            else:
                _errno, errmsg = exc.args
            raise ConnectionError("Error %s while writing to socket. %s." % (
                    _errno, errmsg))
        except:
            # Try to disconnect anyway
            self.disconnect()
            raise

    def send_payload(self):
        "Serialise, sequence, add header, and send payload"
        self.logger.debug(
            "sending payload with outgoing sequence %d", self.outseq)
        # pylint: disable-msg=E1101
        self.out_payload.sequenced.seq = self.outseq
        msg_bytes = self.out_payload.SerializeToString()
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
        # Read a minimum of 4 bytes
        self._fill_buffer()
        result = 0
        shift = 0
        pos = 0
        while 1:
            if pos > len(self._buffer) - 1:
                pos = 0
                # Empty buffer and read another 4 bytes
                self._fill_buffer(4, socket.MSG_WAITALL)
            cbit = ord(self._buffer[pos])
            result |= ((cbit & 0x7f) << shift)
            pos += 1
            if not (cbit & 0x80):
                self._buffer = self._buffer[pos:]
                to_read = max(0, result - len(self._buffer))
                self.logger.debug("next message is %d bytes long", to_read)
                if to_read:
                    # Read the actual message if necessary
                    self._fill_buffer(to_read + len(self._buffer))
                msg_bytes = self._buffer[:result]
                self.logger.debug("parsing bytes %r", msg_bytes)
                msg = self.in_payload
                msg.Clear()
                msg.ParseFromString(msg_bytes)
                # Consume the buffer
                self._buffer = self._buffer[result:]
                return self._handle_in_payload()
            shift += 7

    def _fill_buffer(self, min_size=4, empty=False):
        "Ensure the buffer has at least 4 bytes"
        if empty:
            self._buffer = ''
        while len(self._buffer) < min_size:
            bytes_needed = min_size - len(self._buffer)
            self.logger.debug("receiving %d bytes", bytes_needed)
            bytes = self._sock.recv(bytes_needed, socket.MSG_WAITALL)
            if len(bytes) != bytes_needed:
                self.logger.warning(
                    "socket disconnected while receiving, got %r", bytes)
                self.disconnect()
                raise SocketDisconnected()
            self._buffer += bytes

    def next_frame(self):
        "Get the next frame and increment inseq"
        self.read_frame()
        # pylint: disable-msg=E1101
        payload_in = self.in_payload
        if payload_in.sequenced.seq == self.inseq:
            # Go ahead
            self.logger.debug("received sequence %d", self.inseq)
            self.inseq += 1
            return payload_in
        elif payload_in.sequenced.message_data.replay.seq:
            # Just a replay message, sequence not important
            seq = payload_in.sequenced.message_data.replay.seq
            self.logger.debug(
                "received a replay message with sequence %d", seq)
            return None
        elif payload_in.sequenced.seq > self.inseq:
            # Need a replay
            self.logger.debug(
                "received incoming sequence %d, expected %d",
                payload_in.sequenced.seq,
                self.inseq)
            replay = self.out_payload
            replay.Clear()
            # pylint: disable-msg=E1101
            replay.sequenced.message_data.replay.seq = self.inseq
            self.send_payload()
            return None
        else:
            return None

    def _handle_in_payload(self):
        "Pre-consume the login response message"
        # pylint: disable-msg=E1101
        msg = self.in_payload
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
        ret += chr(0x80 | bits)
        bits = value & 0x7f
        value >>= 7
    return ret + chr(bits)
