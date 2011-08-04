"Different callback classes"


class Callback(object):
    "Represents a collection of callbacks"
    name = '_default'
    def __call__(self, msg):
        self.default(msg)
        # TODO: Actually implement

    def default(self, msg):
        "Abstract default method"
        raise NotImplementedError()


class LoginResponse(Callback):
    name = 'login_response'
    def default(self, msg):
        print "Session", msg.sequenced.message_data.login_response.session


class OrderAccepted(Callback):
    name = 'order_accepted'
    def default(self, msg):
        print "Order Accepted", msg.sequenced.message_data.order_accepted.seq, msg.sequenced.message_data.order_accepted.order


class OrderExecuted(Callback):
    name = 'order_executed'
    def default(self, msg):
        print "Order Executed", msg.sequenced.message_data.order_executed.order, \
            msg.sequenced.message_data.order_executed.price,\
            msg.sequenced.message_data.order_executed.quantity


class OrderCancelled(Callback):
    name = 'order_cancelled'
    def default(self, msg):
        print "Order Cancelled", msg.sequenced.message_data.order_cancelled.order, msg.sequenced.message_data.order_cancelled.reason


class Pong(Callback):
    name = 'pong'
    def default(self, msg):
        print "Pong"


class MarketQuotes(Callback):
    name = 'market_quotes'
    def default(self, msg):
        print "Quotes ", msg.sequenced.message_data.market_quotes.group
