import datetime
import unittest

import smarkets.eto.piqi_pb2 as eto
import smarkets.seto.piqi_pb2 as seto
import smarkets as smk


class SessionTestCase(unittest.TestCase):
    ping_total = 1000
    ping_each = 100
    market_id = smk.Smarkets.str_to_uuid128('1dc91c024')
    contract_id = smk.Smarkets.str_to_uuid128('2ab9acccc')
    price = 2500 # 25.00%
    quantity = 400000 # 40GBP
    side = seto.SIDE_BUY
    username = 'hunter.morris@smarkets.com'
    password = 'abc,123'

    def get_session(self, cls=None):
        if cls is None:
            cls = smk.Session
        return cls(self.username, self.password)

    def get_client(self, cls=None, session=None, session_cls=None):
        if cls is None:
            cls = smk.Smarkets
        if session is None:
            session = self.get_session(cls=session_cls)
        return cls(session)

    def setUp(self):
        self.client = self.get_client()
        self.assertFalse(self.client.session.connected)
        self.assertTrue(self.client.session.session is None)

    def tearDown(self):
        self.client.logout()
        self.client = None

    def _do_login(self):
        # We must start with a clean seq #1
        self.assertEquals(self.client.session.outseq, 1)
        self.assertEquals(self.client.session.inseq, 1)
        self.client.login()
        # Should only have login, then login_response
        self.assertEquals(self.client.session.outseq, 2)
        self.assertEquals(self.client.session.inseq, 2)

    def _simple_cb(self, name):
        msg = seto.Payload()
        def _inner_cb(recv_msg):
            # Copy message in callback to the outer context
            msg.Clear()
            msg.CopyFrom(recv_msg)
        self.client.add_handler(name, _inner_cb)
        # Should be an empty message
        self.assertEquals(msg.eto_payload.type, eto.PAYLOAD_NONE)
        # Return message for comparison
        return msg

    def test_invalid_callback(self):
        # Trying to add a non-existent callback will punish you with a
        # InvalidCallbackError
        self.assertRaises(
            smk.InvalidCallbackError,
            self.client.add_handler, 'baz', lambda _: None)
        self.assertRaises(
            ValueError,
            self.client.add_handler, 'eto.login', None)

    def test_invalid_global_callback(self):
        # Trying to add a 'None' callback will punish you with a
        # ValueError
        self.assertRaises(ValueError, self.client.add_global_handler, None)

    def test_login(self):
        login_response_msg = self._simple_cb('eto.login_response')
        self.assertEquals(self.client.session.outseq, 1)
        self.assertEquals(self.client.session.inseq, 1)
        self.assertTrue(self.client.session.session is None)
        # Send login message and immediately read response; this
        # blocks until the login_response message is received
        self.client.login()
        self.assertFalse(self.client.session.session is None)
        self.assertEquals(
            login_response_msg.type,
            seto.PAYLOAD_ETO)
        self.assertEquals(
            login_response_msg.eto_payload.type,
            eto.PAYLOAD_LOGIN_RESPONSE)
        self.assertEquals(self.client.session.outseq, 2)
        self.assertEquals(self.client.session.inseq, 2)

    def test_ping(self):
        self._do_login()
        pong_msg = self._simple_cb('eto.pong')
        self.client.ping()
        self.assertEquals(self.client.session.outseq, 3)
        self.client.read()
        self.assertEquals(self.client.session.inseq, 3)
        self.assertEquals(
            pong_msg.type,
            seto.PAYLOAD_ETO)
        self.assertEquals(
            pong_msg.eto_payload.type,
            eto.PAYLOAD_PONG)

    def test_ping_many(self):
        self._do_login()
        for seq in xrange(3, self.ping_total + 3, self.ping_each):
            for offset in xrange(0, self.ping_each):
                self.client.ping()
                self.assertEquals(self.client.session.outseq, seq + offset)
            for offset in xrange(0, self.ping_each):
                self.client.read()
                self.assertEquals(self.client.session.inseq, seq + offset)

    def test_order_accepted(self):
        self._do_login()
        order_accepted_msg = self._simple_cb('seto.order_accepted')
        self.client.order(
            self.quantity,
            self.price,
            self.side,
            self.market_id,
            self.contract_id)
        self.assertEquals(self.client.session.outseq, 3)
        self.client.read() # should be accepted
        self.assertEquals(self.client.session.inseq, 3)
        self.assertEquals(
            order_accepted_msg.type,
            seto.PAYLOAD_ORDER_ACCEPTED)
        # Order create message was #2
        self.assertEquals(order_accepted_msg.order_accepted.seq, 2)
        self.assertEquals(order_accepted_msg.order_accepted.order.high, 0)
        self.assertTrue(order_accepted_msg.order_accepted.order.low > 0)

    def test_market_subscription(self):
        self._do_login()
        market_quotes_msg = self._simple_cb('seto.market_quotes')
        self.client.subscribe(self.market_id)
        self.assertEquals(self.client.session.outseq, 3)
        self.client.read() # should be market quotes
        self.assertEquals(self.client.session.inseq, 3)
        self.assertEquals(
            market_quotes_msg.type,
            seto.PAYLOAD_MARKET_QUOTES)
        self.assertEquals(
            market_quotes_msg.market_quotes.market.low, self.market_id.low)
        self.assertEquals(
            market_quotes_msg.market_quotes.market.high, self.market_id.high)

    def test_market_unsubscription(self):
        self._do_login()
        self.client.unsubscribe(self.market_id)
        self.assertEquals(self.client.session.outseq, 3)

    def test_order_cancel(self):
        self._do_login()
        order_accepted_msg = self._simple_cb('seto.order_accepted')
        order_cancelled_msg = self._simple_cb('seto.order_cancelled')
        self.client.order(
            self.quantity,
            self.price,
            self.side,
            self.market_id,
            self.contract_id)
        self.assertEquals(self.client.session.outseq, 3)
        self.client.read() # should be accepted
        self.assertEquals(self.client.session.inseq, 3)
        self.assertEquals(
            order_accepted_msg.type,
            seto.PAYLOAD_ORDER_ACCEPTED)
        # Order create message was #2
        self.assertEquals(order_accepted_msg.order_accepted.seq, 2)
        self.assertEquals(order_accepted_msg.order_accepted.order.high, 0)
        self.assertTrue(order_accepted_msg.order_accepted.order.low > 0)
        # Send a cancel
        self.client.order_cancel(order_accepted_msg.order_accepted.order)
        self.assertEquals(self.client.session.outseq, 4)
        self.client.read() # should be cancelled
        self.assertEquals(self.client.session.inseq, 4)
        self.assertEquals(
            order_cancelled_msg.type,
            seto.PAYLOAD_ORDER_CANCELLED)
        self.assertEquals(
            order_cancelled_msg.order_cancelled.order.high,
            order_accepted_msg.order_accepted.order.high)
        self.assertEquals(
            order_cancelled_msg.order_cancelled.order.low, 
            order_accepted_msg.order_accepted.order.low)

    def test_order_cancel_many(self):
        self._do_login()
        order_accepted_msg = self._simple_cb('seto.order_accepted')
        order_cancelled_msg = self._simple_cb('seto.order_cancelled')
        to_cancel = []
        # Place 100 orders then cancel them
        for _ in xrange(1, 100):
            self.client.order(
                self.quantity / 100,
                self.price,
                self.side,
                self.market_id,
                self.contract_id)
            self.client.read() # should be accepted
            self.assertEquals(
                order_accepted_msg.type,
                seto.PAYLOAD_ORDER_ACCEPTED)
            order_id = seto.Uuid128()
            order_id.CopyFrom(order_accepted_msg.order_accepted.order)
            to_cancel.append(order_id)
            order_accepted_msg.Clear()
        for order_id in to_cancel:
            # Send a cancel
            self.client.order_cancel(order_id)
            self.client.read() # should be cancelled
            self.assertEquals(
                order_cancelled_msg.type,
                seto.PAYLOAD_ORDER_CANCELLED)
            self.assertEquals(
                order_cancelled_msg.order_cancelled.order, order_id)
            order_cancelled_msg.Clear()

    def _event_found_request(self, event_request):
        self._do_login()
        http_found_msg = self._simple_cb('seto.http_found')
        self.client.request_events(event_request)
        self.assertEquals(self.client.session.outseq, 3)
        self.client.read() # should be accepted
        self.assertEquals(self.client.session.inseq, 3)
        self.assertEquals(http_found_msg.type, seto.PAYLOAD_HTTP_FOUND)
        self.assertTrue(http_found_msg.http_found.url is not None)
        self.assertEquals(http_found_msg.http_found.seq, 2)
        listing = self.client.fetch_http_found(http_found_msg)
        self.assertTrue(listing is not None)

    def _event_not_found_request(self, event_request):
        self._do_login()
        invalid_request_msg = self._simple_cb('seto.invalid_request')
        self.client.request_events(event_request)
        self.assertEquals(self.client.session.outseq, 3)
        self.client.read() # should be accepted
        self.assertEquals(self.client.session.inseq, 3)
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
