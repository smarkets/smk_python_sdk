"Smarkets API client"
import logging

from itertools import chain

import eto.piqi_pb2
import seto.piqi_pb2


_ETO_PAYLOAD_TYPES = dict((
    (getattr(eto.piqi_pb2, x),
     'eto.%s' % x.replace('PAYLOAD_', '').lower()) \
        for x in dir(eto.piqi_pb2) if x.startswith('PAYLOAD_')))


_SETO_PAYLOAD_TYPES = dict((
    (getattr(seto.piqi_pb2, x),
     'seto.%s' % x.replace('PAYLOAD_', '').lower()) \
        for x in dir(seto.piqi_pb2) if x.startswith('PAYLOAD_')))


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

    def fire(self, msg):
        "Raise the signal to the handlers"
        for handler in self._handlers:
            handler(msg)

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

    def __init__(self, session):
        self.session = session
        self.callbacks = self.__class__.CALLBACKS.copy()

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

    def order(self, qty, price, side, market_id, contract_id):
        "Create a new order"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.type = seto.piqi_pb2.PAYLOAD_ORDER_CREATE
        msg.order_create.type = seto.piqi_pb2.ORDER_CREATE_LIMIT
        _str_to_uuid128(market_id, msg.order_create.market)
        _str_to_uuid128(contract_id, msg.order_create.contract)
        msg.order_create.side = side
        msg.order_create.quantity_type = seto.piqi_pb2.QUANTITY_PAYOFF_CURRENCY
        msg.order_create.quantity = qty
        msg.order_create.display_quantity = qty
        msg.order_create.price_type = seto.piqi_pb2.PRICE_PERCENT_ODDS
        msg.order_create.price = price
        self._send()

    def order_cancel(self, order_id):
        "Cancel an existing order"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.type = seto.piqi_pb2.PAYLOAD_ORDER_CANCEL
        _str_to_uuid128(order_id, msg.order_cancel.order)
        self._send()

    def ping(self):
        "Ping the service"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.type = seto.piqi_pb2.PAYLOAD_ETO
        msg.eto_payload.type = eto.piqi_pb2.PAYLOAD_PING
        self._send()

    def subscribe(self, market_id):
        "Subscribe to a market"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.type = seto.piqi_pb2.PAYLOAD_MARKET_SUBSCRIPTION
        _str_to_uuid128(market_id, msg.market_subscription.market)
        self._send()

    def unsubscribe(self, market_id):
        "Unsubscribe from a market"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.type = seto.piqi_pb2.PAYLOAD_MARKET_UNSUBSCRIPTION
        _str_to_uuid128(market_id, msg.market_unsubscription.market)
        self._send()

    def add_handler(self, name, callback):
        "Add a callback handler"
        self.callbacks[name] += callback

    def del_handler(self, name, callback):
        "Remove a callback handler"
        self.callbacks[name] -= callback

    def _send(self):
        "Send a payload via the session"
        self.session.send()

    def _dispatch(self, msg):
        "Dispatch a frame to the callbacks"
        name = _SETO_PAYLOAD_TYPES.get(msg.type)
        if name == 'seto.eto':
            name = _ETO_PAYLOAD_TYPES.get(msg.eto_payload.type)
        if name in self.callbacks:
            self.logger.info("dispatching callback %s", name)
            callback = self.callbacks.get(name)
            if callback is not None:
                self.logger.error("no callback %s", name)
                callback(msg)
        else:
            self.logger.info("ignoring unknown message: %s", name)


def _str_to_uuid128(uuid_str, uuid128, strip_tag=True):
    "Convert a string to a uuid128"
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
