"Smarkets API client"
import logging

from itertools import chain

import eto.piqi_pb2 as eto
import seto.piqi_pb2 as seto

from exceptions import InvalidCallbackError


_ETO_PAYLOAD_TYPES = dict((
    (getattr(eto, x),
     'eto.%s' % x.replace('PAYLOAD_', '').lower()) \
        for x in dir(eto) if x.startswith('PAYLOAD_')))


_SETO_PAYLOAD_TYPES = dict((
    (getattr(seto, x),
     'seto.%s' % x.replace('PAYLOAD_', '').lower()) \
        for x in dir(seto) if x.startswith('PAYLOAD_')))


class Callback(object):
    "Container for callbacks"
    def __init__(self):
        self._handlers = set()

    def handle(self, handler):
        "Add a handler to the set of handlers"
        self._handlers.add(handler)
        return self

    def unhandle(self, handler):
        "Remove a handler from the set of handlers"
        try:
            self._handlers.remove(handler)
        except KeyError:
            raise ValueError(
                "Callback is not handling this signal, "
                "so it cannot unhandle it")
        return self

    def fire(self, msg, name=None):
        "Raise the signal to the handlers"
        for handler in self._handlers:
            if name is None:
                handler(msg)
            else:
                handler(name, msg)

    def __len__(self):
        return len(self._handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire


class Smarkets(object):
    """
    Smarkets API implementation

    Provides a simple interface wrapping the protobufs.
    """
    CALLBACKS = dict(((name, Callback()) for name in chain(
                _ETO_PAYLOAD_TYPES.itervalues(),
                _SETO_PAYLOAD_TYPES.itervalues())))

    logger = logging.getLogger('smk.smarkets')

    def __init__(self, session, auto_flush=True):
        self.session = session
        self.auto_flush = auto_flush
        self.callbacks = self.__class__.CALLBACKS.copy()
        self.global_callback = Callback()

    def login(self, receive=True):
        "Connect and ensure the session is active"
        self.session.connect()
        if receive:
            self.read()

    def logout(self):
        "Disconnect. TODO: send logout message before"
        self.session.disconnect()

    def read(self):
        "Receive the next payload and block"
        frame = self.session.next_frame()
        if frame:
            self._dispatch(frame)

    def flush(self):
        "Flush the send buffer"
        self.session.flush()

    def order(self, qty, price, side, market, contract):
        "Create a new order"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.type = seto.PAYLOAD_ORDER_CREATE
        msg.order_create.type = seto.ORDER_CREATE_LIMIT
        msg.order_create.market.CopyFrom(market)
        msg.order_create.contract.CopyFrom(contract)
        msg.order_create.side = side
        msg.order_create.quantity_type = seto.QUANTITY_PAYOFF_CURRENCY
        msg.order_create.quantity = qty
        msg.order_create.price_type = seto.PRICE_PERCENT_ODDS
        msg.order_create.price = price
        self._send()

    def order_cancel(self, order):
        "Cancel an existing order"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.type = seto.PAYLOAD_ORDER_CANCEL
        msg.order_cancel.order.CopyFrom(order)
        self._send()

    def ping(self):
        "Ping the service"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.type = seto.PAYLOAD_ETO
        msg.eto_payload.type = eto.PAYLOAD_PING
        self._send()

    def subscribe(self, market):
        "Subscribe to a market"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.type = seto.PAYLOAD_MARKET_SUBSCRIPTION
        msg.market_subscription.market.CopyFrom(market)
        self._send()

    def unsubscribe(self, market):
        "Unsubscribe from a market"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.type = seto.PAYLOAD_MARKET_UNSUBSCRIPTION
        msg.market_unsubscription.market.CopyFrom(market)
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
        "Send a payload via the session"
        self.session.send(self.auto_flush)

    def _dispatch(self, msg):
        "Dispatch a frame to the callbacks"
        name = _SETO_PAYLOAD_TYPES.get(msg.type)
        if name == 'seto.eto':
            name = _ETO_PAYLOAD_TYPES.get(msg.eto_payload.type)
        if name in self.callbacks:
            self.logger.info("dispatching callback %s", name)
            callback = self.callbacks.get(name)
            if callback is not None:
                callback(msg)
            else:
                self.logger.error("no callback %s", name)
        else:
            self.logger.info("ignoring unknown message: %s", name)
        self.global_callback(msg, name=name)
