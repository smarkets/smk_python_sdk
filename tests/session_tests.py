import datetime
import random
import unittest

from collections import defaultdict

import smarkets.eto.piqi_pb2 as eto
import smarkets.seto.piqi_pb2 as seto
import smarkets as smk

from smarkets.orders import OrderCreate, BUY


class SessionTestCase(unittest.TestCase):

    "Base class for session tests"
    markets = None
    passwords = None
    host = None
    port = None

    def __init__(self, *args, **kwargs):
        self.clients = []
        super(SessionTestCase, self).__init__(*args, **kwargs)

    def get_session(self, user_index, cls=None):
        if cls is None:
            cls = smk.Session
        username = 'none@domain.invalid'
        password = 'none'
        if self.passwords:
            username, password = self.passwords[user_index]
        settings = smk.SessionSettings(username, password)
        if self.host is not None:
            settings.host = self.host
        if self.port is not None:
            settings.port = self.port
        if self.ssl is not None:
            settings.ssl = self.ssl
        return cls(settings)

    def get_client(
            self, cls=None, session=None, session_cls=None, user_index=0):
        if cls is None:
            cls = smk.Smarkets
        if session is None:
            session = self.get_session(user_index, cls=session_cls)
        return cls(session)

    def get_market(self, index=None):
        if index is None:
            index = random.randint(0, len(self.market_list) - 1)
        return self.market_list[index]

    def setUp(self):
        if self.passwords is not None:
            for i in xrange(0, len(self.passwords)):
                self.clients.append(self.get_client(user_index=i))
        else:
            self.clients.append(self.get_client())
        for client in self.clients:
            self.assertFalse(client.session.connected)
            self.assertTrue(client.session.session is None)
        market_dict = defaultdict(list)
        if self.markets:
            for market, contract in self.markets:
                market_dict[market].append(contract)
        market_list = []
        for market, contracts in market_dict.iteritems():
            market_list.append(
                (smk.Smarkets.str_to_uuid128(market),
                 [smk.Smarkets.str_to_uuid128(x) for x in contracts]))
        self.market_list = market_list
        for client in self.clients:
            self.assertEquals(client.session.outseq, 1)
            self.assertEquals(client.session.inseq, 1)
            client.login()
            # Should only have login, then login_response
            self.assertEquals(client.session.outseq, 2)
            self.assertEquals(client.session.inseq, 2)

    def tearDown(self):
        for client in self.clients:
            client.logout()
        self.clients = []

    def _simple_cb(self, client, name):
        msg = seto.Payload()

        def _inner_cb(recv_msg):
            # Copy message in callback to the outer context
            msg.Clear()
            msg.CopyFrom(recv_msg)
        client.add_handler(name, _inner_cb)
        # Should be an empty message
        self.assertEquals(msg.eto_payload.type, eto.PAYLOAD_NONE)
        # Return message for comparison
        return msg


class LoginTestCase(SessionTestCase):

    "Test basic login/login response"

    def setUp(self):
        # Skip defaults
        pass

    def tearDown(self):
        # Skip defaults
        pass

    def test_login(self):
        client = self.get_client()
        login_response_msg = self._simple_cb(client, 'eto.login_response')
        self.assertEquals(client.session.outseq, 1)
        self.assertEquals(client.session.inseq, 1)
        self.assertTrue(client.session.session is None)
        # Send login message and immediately read response; this
        # blocks until the login_response message is received
        client.login()
        self.assertFalse(client.session.session is None)
        self.assertEquals(
            login_response_msg.type,
            seto.PAYLOAD_ETO)
        self.assertEquals(
            login_response_msg.eto_payload.type,
            eto.PAYLOAD_LOGIN_RESPONSE)
        self.assertEquals(client.session.outseq, 2)
        self.assertEquals(client.session.inseq, 2)
        client.logout()


class PingTestCase(SessionTestCase):

    "Test ping/pong"
    ping_total = 1000
    ping_each = 100

    def test_ping(self):
        pong_msg = self._simple_cb(self.clients[0], 'eto.pong')
        self.assertEquals(self.clients[0].ping(), 2)
        self.assertEquals(self.clients[0].session.outseq, 3)
        self.clients[0].read()
        self.assertEquals(self.clients[0].session.inseq, 3)
        self.assertEquals(
            pong_msg.type,
            seto.PAYLOAD_ETO)
        self.assertEquals(
            pong_msg.eto_payload.type,
            eto.PAYLOAD_PONG)

    def test_ping_many(self):
        for seq in xrange(3, self.ping_total + 3, self.ping_each):
            for offset in xrange(0, self.ping_each):
                self.assertEquals(self.clients[0].ping(), seq + offset - 1)
                self.assertEquals(self.clients[0].session.outseq, seq + offset)
            for offset in xrange(0, self.ping_each):
                self.clients[0].read()
                self.assertEquals(self.clients[0].session.inseq, seq + offset)


class OrderTestCase(SessionTestCase):

    "Test simple order placement and cancellation"

    def _test_order(self):
        "Generate a test order"
        market_id, contract_ids = self.get_market(0)
        contract_id = contract_ids[0]
        order = OrderCreate()
        order.quantity = 400000
        order.price = 2500
        order.side = BUY
        order.market = market_id
        order.contract = contract_id
        order.validate_new()
        return order

    def test_order_accepted(self):
        order_accepted_msg = self._simple_cb(
            self.clients[0], 'seto.order_accepted')
        self.assertEquals(
            self.clients[0].order(self._test_order()),
            2)
        self.assertEquals(self.clients[0].session.outseq, 3)
        self.clients[0].read()  # should be accepted
        self.assertEquals(self.clients[0].session.inseq, 3)
        self.assertEquals(
            order_accepted_msg.type,
            seto.PAYLOAD_ORDER_ACCEPTED)
        # Order create message was #2
        self.assertEquals(order_accepted_msg.order_accepted.seq, 2)
        self.assertTrue(order_accepted_msg.order_accepted.order.high >= 0)
        self.assertTrue(order_accepted_msg.order_accepted.order.low > 0)

    def test_order_rejected(self):
        order_rejected_msg = self._simple_cb(
            self.clients[0], 'seto.order_rejected')
        order = self._test_order()
        order.quantity = 50000000  # should be insufficient funds
        order.validate_new()
        self.assertEquals(
            self.clients[0].order(order), 2)
        self.assertEquals(self.clients[0].session.outseq, 3)
        self.clients[0].read()  # should be rejected
        self.assertEquals(self.clients[0].session.inseq, 3)
        self.assertEquals(
            order_rejected_msg.type,
            seto.PAYLOAD_ORDER_REJECTED)
        # Order create message was #2
        self.assertEquals(order_rejected_msg.order_rejected.seq, 2)
        self.assertEquals(
            order_rejected_msg.order_rejected.reason,
            seto.ORDER_REJECTED_INSUFFICIENT_FUNDS)

    def test_order_invalid(self):
        order_invalid_msg = self._simple_cb(
            self.clients[0], 'seto.order_invalid')
        order = self._test_order()
        order.quantity = 500000001  # should be invalid
        order.validate_new()
        self.assertEquals(
            self.clients[0].order(order), 2)
        self.assertEquals(self.clients[0].session.outseq, 3)
        self.clients[0].read()  # should be invalid
        self.assertEquals(self.clients[0].session.inseq, 3)
        self.assertEquals(
            order_invalid_msg.type,
            seto.PAYLOAD_ORDER_INVALID)
        # Order create message was #2
        self.assertEquals(order_invalid_msg.order_invalid.seq, 2)
        self.assertEquals(
            order_invalid_msg.order_invalid.reasons,
            [seto.ORDER_INVALID_INVALID_QUANTITY])

    def test_order_cancel(self):
        order_accepted_msg = self._simple_cb(
            self.clients[0], 'seto.order_accepted')
        order_cancelled_msg = self._simple_cb(
            self.clients[0], 'seto.order_cancelled')
        self.assertEquals(
            self.clients[0].order(self._test_order()),
            2)
        self.assertEquals(self.clients[0].session.outseq, 3)
        self.clients[0].read()  # should be accepted
        self.assertEquals(self.clients[0].session.inseq, 3)
        self.assertEquals(
            order_accepted_msg.type,
            seto.PAYLOAD_ORDER_ACCEPTED)
        # Order create message was #2
        self.assertEquals(order_accepted_msg.order_accepted.seq, 2)
        self.assertTrue(order_accepted_msg.order_accepted.order.high >= 0)
        self.assertTrue(order_accepted_msg.order_accepted.order.low > 0)
        # Send a cancel
        self.assertEquals(
            self.clients[0].order_cancel(
                order_accepted_msg.order_accepted.order),
            3)
        self.assertEquals(self.clients[0].session.outseq, 4)
        self.clients[0].read()  # should be cancelled
        self.assertEquals(self.clients[0].session.inseq, 4)
        self.assertEquals(
            order_cancelled_msg.type,
            seto.PAYLOAD_ORDER_CANCELLED)
        self.assertEquals(
            order_cancelled_msg.order_cancelled.order,
            order_accepted_msg.order_accepted.order)

    def test_order_cancel_many(self):
        order_accepted_msg = self._simple_cb(
            self.clients[0], 'seto.order_accepted')
        order_cancelled_msg = self._simple_cb(
            self.clients[0], 'seto.order_cancelled')
        to_cancel = []
        market_id, contract_ids = self.get_market(0)
        contract_id = contract_ids[0]
        # Place 100 orders then cancel them
        for _ in xrange(1, 100):
            order = self._test_order()
            order.quantity = 4000
            order.validate_new()
            self.clients[0].order(order)
            self.clients[0].read()  # should be accepted
            self.assertEquals(
                order_accepted_msg.type,
                seto.PAYLOAD_ORDER_ACCEPTED)
            order_id = seto.Uuid128()
            order_id.CopyFrom(order_accepted_msg.order_accepted.order)
            to_cancel.append(order_id)
            order_accepted_msg.Clear()
        for order_id in to_cancel:
            # Send a cancel
            self.clients[0].order_cancel(order_id)
            self.clients[0].read()  # should be cancelled
            self.assertEquals(
                order_cancelled_msg.type,
                seto.PAYLOAD_ORDER_CANCELLED)
            self.assertEquals(
                order_cancelled_msg.order_cancelled.order, order_id)
            order_cancelled_msg.Clear()

    def test_order_cancel_rejected(self):
        order_cancel_rejected_msg = self._simple_cb(
            self.clients[0], 'seto.order_cancel_rejected')
        # Send a cancel
        self.assertEquals(
            self.clients[0].order_cancel(self.clients[0].str_to_uuid128('1fff0')),
            2)
        self.assertEquals(self.clients[0].session.outseq, 3)
        self.clients[0].read()  # should be cancel rejected -- order not found
        self.assertEquals(self.clients[0].session.inseq, 3)
        self.assertEquals(
            order_cancel_rejected_msg.type,
            seto.PAYLOAD_ORDER_CANCEL_REJECTED)
        self.assertEquals(
            order_cancel_rejected_msg.order_cancel_rejected.reason,
            seto.ORDER_CANCEL_REJECTED_NOT_FOUND)
        self.assertEquals(
            order_cancel_rejected_msg.order_cancel_rejected.seq, 2)

    def test_multiple_order_cancel_rejected(self):
        order_cancel_rejected_msg = self._simple_cb(
            self.clients[0], 'seto.order_cancel_rejected')
        # Send a cancel
        order_id = self.clients[0].str_to_uuid128('1fff0')
        for i in xrange(3, 10):
            self.assertEquals(
                self.clients[0].order_cancel(order_id),
                i - 1)
            self.assertEquals(self.clients[0].session.outseq, i)
        for i in xrange(3, 10):
            self.clients[0].read()
            self.assertEquals(self.clients[0].session.inseq, i)
            self.assertEquals(
                order_cancel_rejected_msg.type,
                seto.PAYLOAD_ORDER_CANCEL_REJECTED)
            self.assertEquals(
                order_cancel_rejected_msg.order_cancel_rejected.reason,
                seto.ORDER_CANCEL_REJECTED_NOT_FOUND)
            self.assertEquals(
                order_cancel_rejected_msg.order_cancel_rejected.seq, i - 1)

    def test_order_not_live_cancel_rejected(self):
        order_accepted_msg = self._simple_cb(
            self.clients[0], 'seto.order_accepted')
        order_cancelled_msg = self._simple_cb(
            self.clients[0], 'seto.order_cancelled')
        order_cancel_rejected_msg = self._simple_cb(
            self.clients[0], 'seto.order_cancel_rejected')
        market_id, contract_ids = self.get_market(0)
        contract_id = contract_ids[0]
        self.assertEquals(
            self.clients[0].order(self._test_order()),
            2)
        self.assertEquals(self.clients[0].session.outseq, 3)
        self.clients[0].read()  # should be accepted
        self.assertEquals(self.clients[0].session.inseq, 3)
        self.assertEquals(
            order_accepted_msg.type,
            seto.PAYLOAD_ORDER_ACCEPTED)
        # Order create message was #2
        self.assertEquals(order_accepted_msg.order_accepted.seq, 2)
        self.assertTrue(order_accepted_msg.order_accepted.order.high >= 0)
        self.assertTrue(order_accepted_msg.order_accepted.order.low > 0)
        # Send a cancel
        self.assertEquals(
            self.clients[0].order_cancel(order_accepted_msg.order_accepted.order),
            3)
        self.assertEquals(self.clients[0].session.outseq, 4)
        self.clients[0].read()  # should be cancelled
        self.assertEquals(self.clients[0].session.inseq, 4)
        self.assertEquals(
            order_cancelled_msg.type,
            seto.PAYLOAD_ORDER_CANCELLED)
        self.assertEquals(
            order_cancelled_msg.order_cancelled.order,
            order_accepted_msg.order_accepted.order)
        # Send two cancels to be rejected
        self.assertEquals(
            self.clients[0].order_cancel(order_accepted_msg.order_accepted.order),
            4)
        self.assertEquals(self.clients[0].session.outseq, 5)
        self.assertEquals(
            self.clients[0].order_cancel(order_accepted_msg.order_accepted.order),
            5)
        self.assertEquals(self.clients[0].session.outseq, 6)
        self.clients[0].read()  # should be cancel rejected -- order not live
        self.assertEquals(self.clients[0].session.inseq, 5)
        self.assertEquals(
            order_cancel_rejected_msg.type,
            seto.PAYLOAD_ORDER_CANCEL_REJECTED)
        self.assertEquals(
            order_cancel_rejected_msg.order_cancel_rejected.reason,
            seto.ORDER_CANCEL_REJECTED_NOT_LIVE)
        self.assertEquals(
            order_cancel_rejected_msg.order_cancel_rejected.seq, 4)
        self.clients[0].read()  # should be 2nd cancel rejected -- order not live
        self.assertEquals(self.clients[0].session.inseq, 6)
        self.assertEquals(
            order_cancel_rejected_msg.type,
            seto.PAYLOAD_ORDER_CANCEL_REJECTED)
        self.assertEquals(
            order_cancel_rejected_msg.order_cancel_rejected.reason,
            seto.ORDER_CANCEL_REJECTED_NOT_LIVE)
        self.assertEquals(
            order_cancel_rejected_msg.order_cancel_rejected.seq, 5)


class QuoteTestCase(SessionTestCase):

    "Test market data requests"

    def test_market_subscription(self):
        market_quotes_msg = self._simple_cb(self.clients[0], 'seto.market_quotes')
        market_id, _ = self.get_market(0)
        self.assertEquals(
            self.clients[0].subscribe(market_id), 2)
        self.assertEquals(self.clients[0].session.outseq, 3)
        self.clients[0].read()  # should be market quotes
        self.assertEquals(self.clients[0].session.inseq, 3)
        self.assertEquals(
            market_quotes_msg.type,
            seto.PAYLOAD_MARKET_QUOTES)
        self.assertEquals(
            market_quotes_msg.market_quotes.market, market_id)

    def test_market_unsubscription(self):
        market_id, _ = self.get_market(0)
        self.assertEquals(
            self.clients[0].unsubscribe(market_id), 2)
        self.assertEquals(self.clients[0].session.outseq, 3)

    def test_quote1(self):
        order_accepted_msg = self._simple_cb(
            self.clients[0], 'seto.order_accepted')
        order_cancelled_msg = self._simple_cb(
            self.clients[0], 'seto.order_cancelled')
        market_quotes_msg = self._simple_cb(
            self.clients[0], 'seto.market_quotes')
        contract_quotes_msg = self._simple_cb(
            self.clients[0], 'seto.contract_quotes')
        market_id, contract_ids = self.get_market(0)
        contract_id = contract_ids[0]
        self.clients[0].subscribe(market_id)
        self.clients[0].read()  # read the market quotes
        self.assertEquals(
            market_quotes_msg.type,
            seto.PAYLOAD_MARKET_QUOTES)
        start_qty = 0
        for contract_quotes in market_quotes_msg.market_quotes.contract_quotes:
            if contract_quotes.contract == contract_id:
                start_qty = contract_quotes.bids[0].quantity
        order = Order()
        order.quantity = 100000
        order.price = 2500
        order.side = Order.BUY
        order.market = market_id
        order.contract = contract_id
        order.validate_new()
        self.clients[0].order(order)
        self.clients[0].read(2)  # could be accepted or market quotes
        self.assertEquals(
            order_accepted_msg.type,
            seto.PAYLOAD_ORDER_ACCEPTED)
        self.assertEquals(
            contract_quotes_msg.type,
            seto.PAYLOAD_CONTRACT_QUOTES)
        self.assertEquals(
            contract_quotes_msg.contract_quotes.bids[0].quantity,
            start_qty + order.quantity)
        contract_quotes_msg.Clear()
        self.clients[0].order_cancel(order_accepted_msg.order_accepted.order)
        self.clients[0].read(2)  # could be accepted or market quotes
        self.assertEquals(
            order_cancelled_msg.type,
            seto.PAYLOAD_ORDER_CANCELLED)
        self.assertEquals(
            order_cancelled_msg.order_cancelled.order,
            order_accepted_msg.order_accepted.order)
        self.assertEquals(
            contract_quotes_msg.contract_quotes.bids[0].quantity,
            start_qty)


class EventTestCase(SessionTestCase):

    "Test various event requests"

    def _event_found_request(self, event_request):
        http_found_msg = self._simple_cb(self.clients[0], 'seto.http_found')
        self.assertEquals(
            self.clients[0].request_events(event_request), 2)
        self.assertEquals(self.clients[0].session.outseq, 3)
        self.clients[0].read()  # should be accepted
        self.assertEquals(self.clients[0].session.inseq, 3)
        self.assertEquals(http_found_msg.type, seto.PAYLOAD_HTTP_FOUND)
        self.assertTrue(http_found_msg.http_found.url is not None)
        self.assertEquals(http_found_msg.http_found.seq, 2)
        listing = self.clients[0].fetch_http_found(http_found_msg)
        self.assertTrue(listing is not None)

    def _event_not_found_request(self, event_request):
        invalid_request_msg = self._simple_cb(self.clients[0], 'seto.invalid_request')
        self.assertEquals(
            self.clients[0].request_events(event_request), 2)
        self.assertEquals(self.clients[0].session.outseq, 3)
        self.clients[0].read()  # should be accepted
        self.assertEquals(self.clients[0].session.inseq, 3)
        self.assertEquals(
            invalid_request_msg.type, seto.PAYLOAD_INVALID_REQUEST)
        self.assertEquals(invalid_request_msg.invalid_request.seq, 2)
        self.assertEquals(
            invalid_request_msg.invalid_request.type,
            seto.INVALID_REQUEST_DATE_OUT_OF_RANGE)

    def test_current_affairs(self):
        self._event_found_request(smk.CurrentAffairs())

    def test_tv_and_entertainment(self):
        self._event_found_request(smk.TvAndEntertainment())

    def test_politics(self):
        self._event_found_request(smk.Politics())

    def test_sport_other(self):
        self._event_found_request(smk.SportOther())

    def test_football_by_date(self):
        self._event_not_found_request(
            smk.FootballByDate(datetime.date(2010, 8, 20)))

    def test_horse_racing_by_date(self):
        self._event_not_found_request(
            smk.HorseRacingByDate(datetime.date(2010, 8, 20)))

    def test_tennis_by_date(self):
        self._event_not_found_request(
            smk.TennisByDate(datetime.date(2010, 8, 20)))
