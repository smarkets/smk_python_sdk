"Smarkets API client order objects"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php

from types import NoneType as _NoneType

from smarkets.streaming_api import seto as _seto

BUY = 1
SELL = 2

MAX_QUANTITY = 2 ** 31 - 1


def references_match(o1, o2):
    o1ref = o1.reference
    o2ref = o2.reference
    return o1ref is not None and o2ref is not None and o1ref == o2ref


class OrderCreate(object):

    "Simple order state with useful exceptions"
    __slots__ = ('quantity', 'price', 'side', 'market', 'contract',
                 'seq', 'client', 'time_in_force', 'reference')

    def __init__(self):
        for k in self.__slots__:
            setattr(self, k, None)

    def validate_new(self):
        "Validate this order's properties as a new instruction"
        if not isinstance(self.price, (int, long)):
            raise ValueError("price must be an integer")
        if self.price < 1:
            raise ValueError("price must be at least 1")
        if self.price > 9999:
            raise ValueError("price cannot exceed 9999")

        if not isinstance(self.quantity, (int, long)):
            raise ValueError("quantity must be an integer")
        if self.quantity < 1000:
            raise ValueError("quantity must be at least 1,000")
        if self.quantity > MAX_QUANTITY:
            raise ValueError("quantity cannot exceed %r" % MAX_QUANTITY)

        if self.side not in (BUY, SELL):
            raise ValueError("side must be one of BUY or SELL")

        if not isinstance(self.market, _seto.Uuid128):
            raise ValueError("market must be a valid _seto.Uuid128")
        if not isinstance(self.contract, _seto.Uuid128):
            raise ValueError("contract must be a valid _seto.Uuid128")
        if not isinstance(self.reference, (_NoneType, int, long)):
            raise ValueError("reference must be either None or an integer")

        if self.time_in_force:
            allowed = _seto._TIMEINFORCETYPE.values
            if self.time_in_force not in [enum.number for enum in allowed]:
                raise ValueError("Time inforce must be one of: %s" % (
                    [enum.name for enum in allowed],))

    def copy_to(self, payload):
        "Copy this order instruction to a message `payload`"
        payload.type = _seto.PAYLOAD_ORDER_CREATE
        payload.order_create.type = _seto.ORDER_CREATE_LIMIT
        payload.order_create.tif = _seto.IMMEDIATE_OR_CANCEL
        payload.order_create.market.CopyFrom(self.market)
        payload.order_create.contract.CopyFrom(self.contract)
        if self.time_in_force:
            payload.order_create.tif = self.time_in_force
        if self.side == BUY:
            payload.order_create.side = _seto.SIDE_BUY
        elif self.side == SELL:
            payload.order_create.side = _seto.SIDE_SELL
        payload.order_create.quantity_type = _seto.QUANTITY_PAYOFF_CURRENCY
        payload.order_create.quantity = self.quantity
        payload.order_create.price_type = _seto.PRICE_PERCENT_ODDS
        payload.order_create.price = self.price

        if self.reference is not None:
            payload.order_create.reference = self.reference

    def __repr__(self):
        return "OrderCreate(price=%r, quantity=%r, side=%r, market=%r, contract=%r)" % (
            self.price, self.quantity, self.side, self.market, self.contract)


class OrderCancel(object):

    """ Message to cancel the specified order"""
    __slots__ = ('uid', 'seq', 'client', 'reference')

    def __init__(self, uid=None):
        for k in self.__slots__:
            setattr(self, k, None)

        self.uid = uid

    def validate_new(self):
        "Validate this order's properties as a new instruction"
        if not isinstance(self.uid, _seto.Uuid128):
            raise ValueError("order uid must be a valid _seto.Uuid128")

    def copy_to(self, payload):
        "Copy this instruction to a message `payload`"
        payload.type = _seto.PAYLOAD_ORDER_CANCEL
        payload.order_cancel.order.CopyFrom(self.uid)


class OrdersForMarket(object):

    """ Message to cancel the specified order"""
    __slots__ = ('market_uid', 'seq')

    def __init__(self, market_uid):
        self.market_uid = market_uid

    def validate_new(self):
        if not isinstance(self.market_uid, _seto.Uuid128):
            raise ValueError("market must be a valid _seto.Uuid128")

    def copy_to(self, payload):
        "Copy this instruction to a message `payload`"
        payload.type = _seto.PAYLOAD_ORDERS_FOR_MARKET_REQUEST
        payload.orders_for_market_request.market.CopyFrom(self.market_uid)
