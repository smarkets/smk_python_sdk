"Smarkets API client"


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
    CALLBACK_NAMES = (
        'login_response',
        'order_accepted',
        'order_executed',
        'order_cancelled',
        'pong',
        'market_quotes',
        )
    CALLBACKS = dict(((name, Callback()) for name in CALLBACK_NAMES))

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

    def order(self, qty, price, side, group, contract):
        "Create a new order"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.sequenced.message_data.order_create.quantity = qty
        msg.sequenced.message_data.order_create.price = price
        msg.sequenced.message_data.order_create.side = side
        msg.sequenced.message_data.order_create.group = group
        msg.sequenced.message_data.order_create.contract = contract
        self._send()

    def order_cancel(self, order):
        "Cancel an existing order"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.sequenced.message_data.order_cancel.order = order
        self._send()

    def ping(self):
        "Ping the service"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.sequenced.message_data.ping = True
        self._send()

    def subscribe(self, group):
        "Subscribe to a market"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.sequenced.message_data.market_subscription.group = group
        self._send()

    def unsubscribe(self, group):
        "Unsubscribe from a market"
        msg = self.session.out_payload
        msg.Clear()
        # pylint: disable-msg=E1101
        msg.message.market_unsubscription.group = group
        self._send()

    def add_handler(self, name, callback):
        "Add a callback handler"
        self.callbacks[name] += callback

    def del_handler(self, name, callback):
        "Remove a callback handler"
        self.callbacks[name] -= callback

    def _send(self):
        "Send a payload via the session"
        self.session.send_payload()

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
