from __future__ import absolute_import, division, print_function, unicode_literals

from nose.tools import eq_

from smarkets.streaming_api.seto import OrderCreate, Payload, PAYLOAD_ORDER_CREATE
from smarkets.streaming_api.utils import int_to_uuid128, set_payload_message


def test_set_payload_message():
    payload = Payload()
    assert payload.type != PAYLOAD_ORDER_CREATE

    oc = OrderCreate(quantity=123456)
    set_payload_message(payload, oc)
    eq_(payload.type, PAYLOAD_ORDER_CREATE)
    eq_(payload.order_create, oc)


def test_int_to_uuid128():
    value = 12345
    uuid = int_to_uuid128(value)
    eq_((uuid.high, uuid.low), (0, value))
