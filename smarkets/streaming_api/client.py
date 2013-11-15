"Smarkets API client"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
import logging

from smarkets.signal import Signal
from smarkets.streaming_api import eto
from smarkets.streaming_api import seto
from smarkets.streaming_api.exceptions import InvalidCallbackError


_ETO_PAYLOAD_TYPES = dict((
    (getattr(eto, x), 'eto.%s' % x.replace('PAYLOAD_', '').lower())
    for x in dir(eto) if x.startswith('PAYLOAD_')
))


_SETO_PAYLOAD_TYPES = dict((
    (getattr(seto, x), 'seto.%s' % x.replace('PAYLOAD_', '').lower())
    for x in dir(seto) if x.startswith('PAYLOAD_')
))


class StreamingAPIClient(object):
    """
    Smarkets API implementation

    Provides a simple interface wrapping the protobufs.
    """
    CALLBACKS = _ETO_PAYLOAD_TYPES.values() + _SETO_PAYLOAD_TYPES.values()

    logger = logging.getLogger(__name__ + '.SETOClient')

    def __init__(self, session, auto_flush=True):
        self.session = session
        self.auto_flush = auto_flush
        self.callbacks = dict((callback_name, Signal())
                              for callback_name in self.__class__.CALLBACKS)
        self.global_callback = Signal()

    def login(self, receive=True):
        "Connect and ensure the session is active"
        self.session.connect()
        if receive:
            self.read()

    def logout(self, receive=True):
        """
        Disconnect and send logout message, optionally waiting for
        confirmation.
        """
        self.session.logout()
        if receive:
            self.read()
        self.session.disconnect()

    @property
    def raw_socket(self):
        """
        Get raw socket used for communication with remote endpoint.

        :rtype: :class:`socket.socket`
        """
        return self.session.raw_socket

    def read(self, num=1):
        "Receive the next `num` payloads and block if needed"
        for _ in xrange(0, num):
            frame = self.session.next_frame()
            if frame:
                self._dispatch(frame)

    def flush(self):
        "Flush the send buffer"
        self.session.flush()

    def send(self, message):
        payload = self.session.out_payload
        payload.Clear()
        message.copy_to(payload)
        self._send()

    def ping(self):
        "Ping the service"
        msg = self.session.out_payload
        msg.Clear()
        msg.type = seto.PAYLOAD_ETO
        msg.eto_payload.type = eto.PAYLOAD_PING
        self._send()

    def subscribe(self, market):
        "Subscribe to a market"
        msg = self.session.out_payload
        msg.Clear()
        msg.type = seto.PAYLOAD_MARKET_SUBSCRIBE
        msg.market_subscribe.market.CopyFrom(market)
        self._send()

    def request_account_state(self):
        "Request Account State"
        msg = self.session.out_payload
        msg.Clear()
        msg.type = seto.PAYLOAD_ACCOUNT_STATE_REQUEST
        self._send()

    def request_orders_for_account(self):
        "Request an account's orders"
        msg = self.session.out_payload
        msg.Clear()
        msg.type = seto.PAYLOAD_ORDERS_FOR_ACCOUNT_REQUEST
        self._send()

    def request_orders_for_market(self, market):
        "Request an account's orders for a market"
        msg = self.session.out_payload
        msg.Clear()
        msg.type = seto.PAYLOAD_ORDERS_FOR_MARKET_REQUEST
        msg.orders_for_market_request.market.CopyFrom(market)
        self._send()

    def unsubscribe(self, market):
        "Unsubscribe from a market"
        msg = self.session.out_payload
        msg.Clear()
        msg.type = seto.PAYLOAD_MARKET_UNSUBSCRIBE
        msg.market_unsubscribe.market.CopyFrom(market)
        self._send()

    def request_events(self, request):
        "Send a structured events request"
        msg = self.session.out_payload
        msg.Clear()
        request.copy_to(msg)
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

    @staticmethod
    def str_to_uuid128(uuid_str, uuid128=None, strip_tag=True):
        "Convert a string to a uuid128"
        if uuid128 is None:
            uuid128 = seto.Uuid128()
        uuid128.Clear()
        if strip_tag:
            uuid_str = uuid_str[:-4]
        low = int(uuid_str[-16:], 16)
        uuid128.low = low
        high = uuid_str[:-16]
        if high:
            high = int(high, 16)
            if high:
                uuid128.high = high
        return uuid128

    @staticmethod
    def copy_payload(payload):
        "Copy a payload and return the copy"
        payload_copy = seto.Payload()
        payload_copy.CopyFrom(payload)
        return payload_copy

    def _send(self):
        """
        Send a payload via the session.
        """
        self.session.send(self.auto_flush)

    def _dispatch(self, message):
        "Dispatch a frame to the callbacks"
        name = _SETO_PAYLOAD_TYPES.get(message.type)
        if name == 'seto.eto':
            name = _ETO_PAYLOAD_TYPES.get(message.eto_payload.type)
        if name in self.callbacks:
            self.logger.debug("dispatching callback %s", name)
            callback = self.callbacks.get(name)
            if callback is not None:
                callback(message)
            else:
                self.logger.error("no callback %s", name)
            self.logger.debug("ignoring unknown message: %s", name)

        self.logger.debug('Dispatching global callbacks for %s', name)
        self.global_callback(name, message)
