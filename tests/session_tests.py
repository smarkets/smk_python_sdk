import unittest

import eto.piqi_pb2
import seto.piqi_pb2
import smk


class SessionTestCase(unittest.TestCase):

    def get_session(self, cls=None):
        if cls is None:
            cls = smk.Session
        return cls('hunter.morris@smarkets.com', 'abc,123')

    def get_client(self, cls=None, session=None, session_cls=None):
        if cls is None:
            cls = smk.Smarkets
        if session is None:
            session = self.get_session(cls=session_cls)
        return cls(session)

    def setUp(self):
        self.client = self.get_client()

    def tearDown(self):
        self.client.logout()

    def test_invalid_callback(self):
        # Trying to add a non-existent callback will punish you with a
        # KeyError
        self.assertRaises(
            smk.InvalidCallbackError,
            lambda: self.client.add_handler('baz', lambda: None))
        self.assertRaises(ValueError,
            lambda: self.client.add_handler('eto.login', None))

    def test_login(self):
        login_response_msg = seto.piqi_pb2.Payload()
        def _login_response_cb(msg):
            # Copy message in callback to the outer context
            login_response_msg.CopyFrom(msg)
        self.client.add_handler('eto.login_response', _login_response_cb)
        self.assertEquals(self.client.session.outseq, 1)
        self.assertEquals(self.client.session.inseq, 1)
        self.assertTrue(self.client.session.session is None)
        self.assertEquals(
            login_response_msg.eto_payload.type,
            eto.piqi_pb2.PAYLOAD_NONE)
        # Send login message and immediately read response; this
        # blocks until the login_response message is received
        self.client.login()
        self.assertFalse(self.client.session.session is None)
        self.assertEquals(
            login_response_msg.eto_payload.type,
            eto.piqi_pb2.PAYLOAD_LOGIN_RESPONSE)
        self.assertEquals(self.client.session.outseq, 2)
        self.assertEquals(self.client.session.inseq, 2)
