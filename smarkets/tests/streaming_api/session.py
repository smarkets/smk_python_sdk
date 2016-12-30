from __future__ import absolute_import, division, print_function, unicode_literals

from nose.tools import eq_
from smarkets.streaming_api.session import SessionSettings, Session


def test_next_frame_regression():
    settings = SessionSettings('username', 'password')
    session = Session(settings)
    session_string = '8zysBBGAD6nb95JDIO'
    session.buffered_incoming_payloads = \
        [bytearray(
            b'\x08\x01\x12\x1e\x08\x01\x10\x08\x18\x002\x16\n\x12' +
            session_string.encode('utf-8') +
            b'\x10\x02'
        )]
    payload = session.next_frame().protobuf
    eq_(payload.eto_payload.login_response.session, session_string)
