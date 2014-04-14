"Smarkets TCP-based session management"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
import logging
import socket
import ssl

from google.protobuf.text_format import MessageToString

from smarkets import private
from smarkets.errors import reraise
from smarkets.lazy import LazyCall
from smarkets.streaming_api import eto, seto
from smarkets.streaming_api.exceptions import ConnectionError, SocketDisconnected
from smarkets.streaming_api.framing import frame_decode_all, frame_encode


class SessionSettings(object):

    "Encapsulate settings necessary to create a new session"

    def __init__(self, username, password, host='api-sandbox.smarkets.com', port=3801, ssl=True,
                 socket_timeout=30, ssl_kwargs=None, tcp_nodelay=True):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.socket_timeout = socket_timeout
        self.ssl = ssl
        self.ssl_kwargs = ssl_kwargs or {}
        self.tcp_nodelay = tcp_nodelay
        # Most message are quite small, so this won't come into
        # effect. For larger messages, it needs some performance
        # testing to determine whether a single large recv() system
        # call is worse than many smaller ones.
        self.read_chunksize = 65536  # 64k


class Session(object):

    "Manages TCP communication via Smarkets streaming API"
    logger = private(logging.getLogger('smarkets.session'))
    flush_logger = private(logging.getLogger('smarkets.session.flush'))

    def __init__(self, settings, inseq=1, outseq=1, account_sequence=None):
        """
        :type setting: :class:`SessionSettings`
        """
        self.settings = settings
        self.account_sequence = account_sequence
        self.socket = SessionSocket(settings)
        self.inseq = inseq
        # Outgoing socket sequence number
        self.outseq = outseq
        # Outgoing buffer sequence number
        self.buf_outseq = outseq
        self.out_payload = seto.Payload()
        self.send_buffer = b''
        self.read_buffer = b''
        self.buffered_incoming_payloads = []

    @property
    def raw_socket(self):
        '''
        Get raw socket used for communication with remote endpoint.
        :rtype: :class:`socket.socket`
        '''
        return self.socket._sock

    @property
    def output_buffer_size(self):
        return len(self.send_buffer)

    @property
    def connected(self):
        "Returns True if the socket is currently connected"
        return self.socket.connected

    def connect(self):
        "Connects to the API and logs in if not already connected"
        if self.socket.connect():
            self._clear_send_buffer()
            # Reset separate outgoing buffer sequence number
            self.buf_outseq = 1
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

            self.send()
            self.flush()

    def _clear_send_buffer(self):
        if self.send_buffer:
            self.logger.warn(
                'Clearing non-empty buffer, %d bytes will be lost: %r',
                len(self.send_buffer), self.send_buffer,
            )
        self.send_buffer = b''

    def logout(self):
        "Disconnects from the API"
        logout = self.out_payload
        logout.Clear()
        logout.type = seto.PAYLOAD_ETO
        logout.eto_payload.type = eto.PAYLOAD_LOGOUT
        logout.eto_payload.logout.reason = eto.LOGOUT_NONE
        self.logger.info("sending logout payload")
        self.send()
        self.flush()

    def disconnect(self):
        "Disconnects from the API"
        self.socket.disconnect()

    def send(self):
        "Serialise, sequence, add header, and send payload"
        self.logger.debug(
            "buffering payload: %s",
            LazyCall(MessageToString, self.out_payload))
        sent_seq = self.buf_outseq
        self.out_payload.eto_payload.seq = sent_seq
        self.send_buffer += frame_encode(self.out_payload.SerializeToString())
        self.buf_outseq += 1

    def flush(self):
        "Flush payloads to the socket"
        self.flush_logger.debug("Flushing %d bytes", len(self.send_buffer))
        if self.send_buffer:
            bytes_sent = self.socket.send(self.send_buffer)
            self.flush_logger.debug("Flushed %d bytes out of %d", bytes_sent, len(self.send_buffer))
            self.send_buffer = self.send_buffer[bytes_sent:]

    def read(self):
        self.read_buffer += self.socket.recv()

        messages, remaining_buffer = frame_decode_all(self.read_buffer)
        self.buffered_incoming_payloads.extend(messages)
        self.read_buffer = remaining_buffer

    def next_frame(self):
        """Get the next payload and increment inseq.

        .. warning::
            Payload returned by `next_frame` has to be consumed before next call to `next_frame` happens.

        :return: A payload or None if no payloads in buffer.

        :rtype: :class:`smarkets.streaming_api.seto.Payload` or None

        """
        if not self.buffered_incoming_payloads:
            return None

        data, self.buffered_incoming_payloads = (
            self.buffered_incoming_payloads[0], self.buffered_incoming_payloads[1:])

        payload = seto.Payload()
        payload.ParseFromString(data)
        self._handle_in_payload(payload)
        if payload.eto_payload.seq == self.inseq:
            # Go ahead
            self.logger.debug("received sequence %d", self.inseq)
            self.inseq += 1
            return payload
        elif payload.eto_payload.seq > self.inseq:
            self.logger.warn(
                'Received incoming sequence %d instead of expected %d',
                payload.eto_payload.seq, self.inseq)
            return None
        else:
            return None

    def _handle_in_payload(self, msg):
        "Pre-consume the login response message"
        self.logger.debug("received message to dispatch: %s", LazyCall(MessageToString, msg))
        if msg.eto_payload.type == eto.PAYLOAD_LOGIN_RESPONSE:
            self.session = msg.eto_payload.login_response.session
            self.buf_outseq = msg.eto_payload.login_response.reset
            self._clear_send_buffer()
            self.logger.info("received login_response with session %r and outseq %d",
                             self.session, self.buf_outseq)
        elif msg.eto_payload.type == eto.PAYLOAD_HEARTBEAT:
            self.logger.debug("received heartbeat message, responding...")
            heartbeat = self.out_payload
            heartbeat.Clear()
            heartbeat.type = seto.PAYLOAD_ETO
            heartbeat.eto_payload.type = eto.PAYLOAD_HEARTBEAT
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
            if self.settings.tcp_nodelay:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
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

    def send(self, data):
        """
        :type data: byte string
        :return: Number of sent bytes
        :rtype: int
        """
        if self._sock is None:
            raise SocketDisconnected('Trying to write to socket when disconnected')
        try:
            self.wire_logger.debug("sending %d bytes: %r", len(data), data)
            sent = self._sock.send(data)
            if sent == 0:
                raise SocketDisconnected('Socket disconnected when writing to it, 0 bytes written')
            return sent
        except socket.error as e:
            reraise(ConnectionError("Error while writing to socket", e))

    def recv(self):
        """Read stuff from underlying socket.

        :rtype: byte string
        """
        if self._sock is None:
            raise SocketDisconnected(
                'Trying to read from a socket when disconnected')

        try:
            inbytes = self._sock.recv(self.settings.read_chunksize)
            if not inbytes:
                message = "Socket disconnected while receiving, got %r" % (inbytes,)
                self.logger.info(message)
                raise SocketDisconnected(message)
            self.wire_logger.debug('Received %d bytes: %r', len(inbytes), inbytes)
            return inbytes
        except socket.error as e:
            reraise(ConnectionError('Error while reading from socket', e))

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
