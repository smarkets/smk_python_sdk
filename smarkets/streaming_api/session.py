"Smarkets TCP-based session management"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
import logging
import Queue
import socket
import types
import ssl

from google.protobuf import text_format

from smarkets import private
from smarkets.errors import reraise
from smarkets.streaming_api import eto, seto
from smarkets.streaming_api.exceptions import ConnectionError, SocketDisconnected


class SessionSettings(object):

    "Encapsulate settings necessary to create a new session"

    def __init__(self, username, password):
        if username is None:
            raise ValueError("username cannot be None")
        if password is None:
            raise ValueError("password cannot be None")
        self.username = username
        self.password = password
        self.host = 'api-sandbox.smarkets.com'
        self.port = 3701
        self.socket_timeout = 30
        self.ssl = True
        self.ssl_kwargs = {}
        # Most message are quite small, so this won't come into
        # effect. For larger messages, it needs some performance
        # testing to determine whether a single large recv() system
        # call is worse than many smaller ones.
        self.read_chunksize = 65536  # 64k

    def validate(self):
        "Do basic validation on the settings"
        if not isinstance(self.socket_timeout, (types.NoneType, int)):
            raise ValueError("socket_timeout must be an integer or None")
        if self.socket_timeout is not None and self.socket_timeout <= 0:
            raise ValueError("socket_timeout must be positive")
        if not isinstance(self.read_chunksize, (types.NoneType, int, long)):
            raise ValueError("read_chunksize must be an integer or None")
        if self.read_chunksize is not None and self.read_chunksize <= 0:
            raise ValueError("read_chunksize must be positive")
        if not isinstance(self.ssl, (bool)):
            raise ValueError("ssl must ba a bool")
        if not isinstance(self.ssl_kwargs, (dict)):
            raise ValueError("ssl_kwargs must be a dict")


class Session(object):

    "Manages TCP communication via Smarkets streaming API"
    logger = private(logging.getLogger('smarkets.session'))
    flush_logger = private(logging.getLogger('smarkets.session.flush'))

    def __init__(self, settings, inseq=1, outseq=1, account_sequence=None):
        if not isinstance(settings, SessionSettings):
            raise ValueError("settings is not a SessionSettings")
        settings.validate()
        self.settings = settings
        self.account_sequence = account_sequence
        self.socket = SessionSocket(settings)
        self.inseq = inseq
        # Outgoing socket sequence number
        self.outseq = outseq
        # Outgoing buffer sequence number
        self.buf_outseq = outseq
        self.in_payload = seto.Payload()
        self.out_payload = seto.Payload()
        self.send_buffer = Queue.Queue()

    @property
    def raw_socket(self):
        '''
        Get raw socket used for communication with remote endpoint.
        :rtype: :class:`socket.socket`
        '''
        return self.socket._sock

    @property
    def connected(self):
        "Returns True if the socket is currently connected"
        return self.socket.connected

    def connect(self):
        "Connects to the API and logs in if not already connected"
        if self.socket.connect():
            # Clear the outgoing send buffer
            self.send_buffer = Queue.Queue()
            # Reset separate outgoing buffer sequence number
            self.buf_outseq = self.outseq
            login = self.out_payload
            login.Clear()
            login.type = seto.PAYLOAD_LOGIN
            login.eto_payload.type = eto.PAYLOAD_LOGIN
            login.login.username = self.settings.username
            login.login.password = self.settings.password
            self.logger.info("sending login payload")
            if self.account_sequence is not None:
                self.logger.info("Attempting to resume session, account sequence %d",
                                 self.account_sequence)
                login.login.account_sequence = self.account_sequence

            # Always flush outgoing login message
            self.send(True)

    def logout(self):
        "Disconnects from the API"
        logout = self.out_payload
        logout.Clear()
        logout.type = seto.PAYLOAD_ETO
        logout.eto_payload.type = eto.PAYLOAD_LOGOUT
        logout.eto_payload.logout.reason = eto.LOGOUT_NONE
        self.logger.info("sending logout payload")
        self.send(True)

    def disconnect(self):
        "Disconnects from the API"
        self.socket.disconnect()

    def send(self, flush=False):
        "Serialise, sequence, add header, and send payload"
        self.logger.debug(
            "buffering payload with outgoing sequence %d: %s",
            self.outseq, text_format.MessageToString(self.out_payload))
        sent_seq = self.buf_outseq
        self.out_payload.eto_payload.seq = sent_seq
        self.send_buffer.put_nowait(self.out_payload.SerializeToString())
        self.buf_outseq += 1
        if flush:
            self.flush()

    def flush(self):
        "Flush payloads to the socket"
        self.flush_logger.debug("flushing %d payloads", self.send_buffer.qsize())
        while not self.send_buffer.empty():
            try:
                msg_bytes = self.send_buffer.get_nowait()
                self.socket.send(msg_bytes)
                self.outseq += 1
            except Queue.Empty:
                break

    def next_frame(self):
        "Get the next frame and increment inseq"
        msg_bytes = self.socket.recv()
        self.in_payload.Clear()
        self.in_payload.ParseFromString(msg_bytes)
        self._handle_in_payload()
        if self.in_payload.eto_payload.seq == self.inseq:
            # Go ahead
            self.logger.debug("received sequence %d", self.inseq)
            self.inseq += 1
            return self.in_payload
        elif self.in_payload.eto_payload.type == eto.PAYLOAD_REPLAY:
            # Just a replay message, sequence not important
            seq = self.in_payload.eto_payload.replay.seq
            self.logger.debug(
                "received a replay message with sequence %d", seq)
            return None
        elif self.in_payload.eto_payload.seq > self.inseq:
            # Need a replay
            self.logger.info(
                "received incoming sequence %d, expected %d, need replay",
                self.in_payload.eto_payload.seq,
                self.inseq)
            replay = self.out_payload
            replay.Clear()
            replay.type = seto.PAYLOAD_ETO
            replay.eto_payload.type = eto.PAYLOAD_REPLAY
            replay.eto_payload.replay.seq = self.inseq
            # Do not auto-flush replay because we may be in another
            # thread
            self.send()
            return None
        else:
            return None

    def _handle_in_payload(self):
        "Pre-consume the login response message"
        msg = self.in_payload
        self.logger.debug(
            "received message to dispatch: %s",
            text_format.MessageToString(msg))
        if msg.eto_payload.type == eto.PAYLOAD_LOGIN_RESPONSE:
            self.session = msg.eto_payload.login_response.session
            self.outseq = msg.eto_payload.login_response.reset
            self.buf_outseq = self.outseq
            self.send_buffer = Queue.Queue()
            self.logger.info("received login_response with session %r and outseq %d",
                             self.session, self.outseq)
        elif msg.eto_payload.type == eto.PAYLOAD_HEARTBEAT:
            self.logger.debug("received heartbeat message, responding...")
            heartbeat = self.out_payload
            heartbeat.Clear()
            heartbeat.type = seto.PAYLOAD_ETO
            heartbeat.eto_payload.type = eto.PAYLOAD_HEARTBEAT
            # Do not immediately flush heartbeat response because we
            # may be in another thread
            self.send()
        return msg


class SessionSocket(object):

    "Wraps a socket with basic framing/deframing"
    logger = private(logging.getLogger('smarkets.session.socket'))
    wire_logger = private(logging.getLogger('smarkets.session.wire'))

    def __init__(self, settings):
        if not isinstance(settings, SessionSettings):
            raise ValueError("settings is not a SessionSettings")
        self.settings = settings
        self._buffer = ''
        self._sock = None

    @property
    def connected(self):
        "Returns True if the socket is currently connected"
        return self._sock is not None

    def connect(self):
        """
        Create a TCP socket connection.

        Returns True if the socket needed connecting, False if not
        """
        if self._sock is not None:
            self.logger.debug("connect() called, but already connected")
            return False
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.settings.ssl:
                sock = ssl.wrap_socket(sock, **self.settings.ssl_kwargs)
            if self.settings.socket_timeout is not None:
                sock.settimeout(self.settings.socket_timeout)
            self.logger.info(
                "connecting with new socket to %s:%s",
                self.settings.host, self.settings.port)
            sock.connect((self.settings.host, self.settings.port))
        except socket.error as exc:
            reraise(ConnectionError(self._error_message(exc)))

        self._sock = sock
        return True

    def disconnect(self):
        "Close the TCP socket."
        if self._sock is None:
            self.logger.debug("disconnect() called with no socket, ignoring")
            return
        try:
            self.logger.info("shutting down reads")
            self._sock.shutdown(socket.SHUT_RD)
            self.logger.info("shutting down reads/writes")
            self._sock.shutdown(socket.SHUT_RDWR)
            self.logger.info("closing socket")
            self._sock.close()
        except socket.error as e:
            # Ignore exceptions while disconnecting
            self.logger.debug('Exception when disconnecting: %r', e)
        self._sock = None

    def send(self, msg_bytes):
        "Send a payload"
        if self._sock is None:
            raise SocketDisconnected('Trying to write to socket when disconnected')
        byte_count = len(msg_bytes)
        # Pad to 4 bytes
        padding = '\x00' * max(0, 3 - byte_count)
        self.logger.debug(
            "payload has %d bytes and needs %d padding",
            byte_count, len(padding))
        frame = _encode_varint(byte_count) + msg_bytes + padding
        try:
            self.wire_logger.debug("sending frame bytes %r", frame)
            self._sock.sendall(frame)
        except socket.error as e:
            reraise(ConnectionError("Error while writing to socket", e))

    def recv(self):
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
                self._fill_buffer(4, True)
            cbit = ord(self._buffer[pos])
            result |= ((cbit & 0x7f) << shift)
            pos += 1
            if not (cbit & 0x80):
                self._buffer = self._buffer[pos:]
                to_read = max(0, result - len(self._buffer))
                self.logger.debug("next message is %d bytes long", to_read)
                if to_read:
                    # Read the actual message if necessary
                    while to_read > self.settings.read_chunksize:
                        self._fill_buffer(
                            self.settings.read_chunksize + len(self._buffer))
                        to_read -= self.settings.read_chunksize
                    if to_read > 0:
                        self._fill_buffer(to_read + len(self._buffer))
                msg_bytes = self._buffer[:result]
                self.wire_logger.debug("received bytes %r", msg_bytes)
                # Consume the buffer
                self._buffer = self._buffer[result:]
                return msg_bytes
            shift += 7

    def _fill_buffer(self, min_size=4, empty=False):
        "Ensure the buffer has at least 4 bytes"
        if self._sock is None:
            raise SocketDisconnected(
                'Trying to read from a socket when disconnected')

        if empty:
            self._buffer = ''
        while len(self._buffer) < min_size:
            bytes_needed = min_size - len(self._buffer)
            self.logger.debug("receiving %d bytes", bytes_needed)
            try:
                if self.settings.ssl:
                    inbytes = self._recv_msg_ssl(bytes_needed)
                else:
                    inbytes = self._recv_msg_sock(bytes_needed)
            except socket.error as e:
                reraise(ConnectionError('Error while reading from socket', e))

            self._buffer += inbytes

    def _recv_msg_sock(self, bytes_needed):
        "Wrap reading from a plain socket"
        inbytes = self._sock.recv(bytes_needed, socket.MSG_WAITALL)
        if len(inbytes) != bytes_needed:
            message = "Socket disconnected while receiving, got %r" % (inbytes,)
            self.logger.info(message)
            raise SocketDisconnected(message)
        return inbytes

    def _recv_msg_ssl(self, bytes_needed):
        "Wrap reading from an SSL socket where we can't pass options to recv"
        msglen = 0
        msglist = []
        while msglen < bytes_needed:
            chunk = self._sock.recv(
                min(self.settings.read_chunksize, bytes_needed - msglen))
            if not chunk:
                message = "Socket disconnected while receiving"
                self.logger.info(message)
                raise SocketDisconnected(message)
            msglist.append(chunk)
            msglen += len(chunk)
        return ''.join(msglist)

    def _error_message(self, exception):
        "Stringify a socket exception"
        # args for socket.error can either be (errno, "message")
        # or just "message"
        if len(exception.args) == 1:
            return "Error connecting to %s:%s. %s." % (
                self.settings.host, self.settings.port, exception.args[0])
        else:
            return "Error %s connecting %s:%s. %s." % (
                exception.args[0], self.settings.host, self.settings.port,
                exception.args[1])


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
