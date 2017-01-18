"Smarkets API client"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
import logging
import sys

from smarkets.signal import Signal
from smarkets.streaming_api import eto
from smarkets.streaming_api import seto
from smarkets.streaming_api.exceptions import InvalidCallbackError
from smarkets.streaming_api.utils import set_payload_message


def _get_payload_types(module):
    module_name = module.__name__.split('.')[-1]

    return dict((
        (getattr(module, x),
         '%s.%s' % (module_name, x.replace('PAYLOAD_', '').lower()))
        for x in dir(module) if x.startswith('PAYLOAD_')
    ))


_ETO_PAYLOAD_TYPES = _get_payload_types(eto)
_SETO_PAYLOAD_TYPES = _get_payload_types(seto)


READ_MODE_BUFFER_FROM_SOCKET = 1
READ_MODE_DISPATCH_FROM_BUFFER = 2
READ_MODE_BUFFER_AND_DISPATCH = READ_MODE_BUFFER_FROM_SOCKET | READ_MODE_DISPATCH_FROM_BUFFER


class StreamingAPIClient(object):

    """
    Smarkets API implementation

    Provides a simple interface wrapping the protobufs.
    """
    CALLBACKS = list(_ETO_PAYLOAD_TYPES.values()) + list(_SETO_PAYLOAD_TYPES.values())

    logger = logging.getLogger(__name__ + '.SETOClient')

    def __init__(self, session):
        self.session = session
        self.callbacks = dict((callback_name, Signal())
                              for callback_name in self.__class__.CALLBACKS)
        self.global_callback = Signal()

    def login(self, receive=True):
        "Connect and ensure the session is active"
        self.session.connect()
        if receive:
            self.read()
            self.flush()

    def logout(self, receive=True):
        """
        Disconnect and send logout message, optionally waiting for
        confirmation.
        """
        self.session.logout()
        if receive:
            self.read()
            self.flush()

        self.session.disconnect()

    @property
    def raw_socket(self):
        """
        Get raw socket used for communication with remote endpoint.

        :rtype: :class:`socket.socket`
        """
        return self.session.raw_socket

    @property
    def output_buffer_size(self):
        return self.session.output_buffer_size

    def read(self, read_mode=READ_MODE_BUFFER_AND_DISPATCH, limit=sys.maxsize):
        """
        .. note::
            This method will block until it can read *any* data from the remote endpoint. It doesn't mean
            it will receive enough data to process it.
        :return: Number of processed incoming messages.
        :rtype: int
        """
        if read_mode & READ_MODE_BUFFER_FROM_SOCKET:
            self.session.read()

        processed = 0
        if read_mode & READ_MODE_DISPATCH_FROM_BUFFER:
            while processed < limit:
                frame = self.session.next_frame()
                if frame:
                    self._dispatch(frame)
                    processed += 1
                else:
                    break

        return processed

    def flush(self):
        "Flush the send buffer"
        self.session.flush()

    def send(self, message):
        payload = self.session.out_payload
        payload.Clear()
        set_payload_message(payload, message)
        self._send()

    def ping(self):
        "Ping the service"
        msg = self.session.out_payload
        msg.Clear()
        msg.type = seto.PAYLOAD_ETO
        msg.eto_payload.type = eto.PAYLOAD_PING
        self._send()

    def add_handler(self, name, callback):
        "Add a callback handler"
        if not hasattr(callback, '__call__'):
            raise ValueError('callback must be a callable')
        if name not in self.callbacks:
            raise InvalidCallbackError(name)
        self.callbacks[name] += callback

    def add_global_handler(self, callback):
        "Add a global callback handler, called for every message"
        if not hasattr(callback, '__call__'):
            raise ValueError('callback must be a callable')
        self.global_callback += callback

    def del_handler(self, name, callback):
        "Remove a callback handler"
        if name not in self.callbacks:
            raise InvalidCallbackError(name)
        self.callbacks[name] -= callback

    def del_global_handler(self, callback):
        "Remove a global callback handler"
        self.global_callback -= callback

    def _send(self):
        """
        Send a payload via the session.
        """
        self.session.send()

    def _dispatch(self, frame):
        "Dispatch a frame to the callbacks"
        message = frame.protobuf
        name = _SETO_PAYLOAD_TYPES.get(message.type, 'seto.unknown')
        if name == 'seto.eto':
            name = _ETO_PAYLOAD_TYPES.get(message.eto_payload.type)
        if name in self.callbacks:
            self.logger.debug("dispatching callback %s", name)
            callback = self.callbacks.get(name)
            if callback is not None:
                callback(message=message)
            else:
                self.logger.error("no callback %s", name)
        else:
            self.logger.debug("ignoring unknown message: %s", name)

        self.logger.debug('Dispatching global callbacks for %s', name)
        self.global_callback(name=name, message=frame)
