import callbacks

from seto_pb2 import payload


class Smarkets(object):
    """
    Smarkets API implementation

    Provides a simple interface wrapping the protobufs.
    """
    CALLBACKS = dict(
        ((x.name, x) for x in [
                callbacks.LoginResponse(),
                callbacks.OrderAccepted(),
                callbacks.OrderExecuted(),
                callbacks.OrderCancelled(),
                callbacks.Pong(),
                callbacks.MarketQuotes()
                ]))

    def __init__(self, session):
        self.session = session
        self.callbacks = self.__class__.CALLBACKS.copy()

    def login(self, receive=True):
        "Connect and ensure the session is active"
        self.session.connect()
        if receive:
            self.read()

    def read(self):
        "Receive the next payload and block"
        frame = self.session.next_frame()
        if frame:
            self._dispatch(frame)
            # XXX: Should I increment here or in the session itself?
            self.session.inseq += 1

    def order(self, qty, price, side, group, contract):
        "Create a new order"
        msg = payload()
        msg.sequenced.message_data.order_create.quantity = qty
        msg.sequenced.message_data.order_create.price = price
        msg.sequenced.message_data.order_create.side = side
        msg.sequenced.message_data.order_create.group = group
        msg.sequenced.message_data.order_create.contract = contract
        self._send(msg)

    def order_cancel(self, order):
        "Cancel an existing order"
        msg = payload()
        msg.sequenced.message_data.order_cancel.order = order
        self._send(msg)

    def ping(self):
        "Ping the service"
        msg = payload()
        msg.sequenced.message_data.ping = True
        self._send(msg)

    def subscribe(self, group):
        "Subscribe to a market"
        msg = payload()
        msg.sequenced.message_data.market_subscription.group = group
        self._send(msg)

    def unsubscribe(self, group):
        "Unsubscribe from a market"
        msg = payload()
        msg.message.market_unsubscription.group = group
        self._send(msg)

    def _send(self, payload_out):
        "Send a payload via the session"
        self.session.send_payload(payload_out)

    def _dispatch(self, msg):
        "Dispatch a frame to the callbacks"
        name = None
        if msg.sequenced.message_data.login_response.session:
            name = 'login_response'
        elif msg.sequenced.message_data.order_accepted.order:
            name = 'order_accepted'
        elif msg.sequenced.message_data.order_executed.order:
            name = 'order_executed'
        elif msg.sequenced.message_data.order_cancelled.order:
            name = 'order_cancelled'
        elif msg.sequenced.message_data.pong:
            name = 'pong'
        elif msg.sequenced.message_data.market_quotes.group:
            name = 'market_quotes'
        if name in self.callbacks:
            callback = self.callbacks[name]
            callback(msg)
