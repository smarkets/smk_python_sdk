"Smarkets API client order objects"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php

import smarkets.seto.piqi_pb2 as seto

BUY = 1
SELL = 2


class OrderCreate(object):
    "Simple order state with useful exceptions"
    __slots__ = ('quantity', 'price', 'side', 'market', 'contract',
                    'accept_callback', 'reject_callback', 'invalid_callback', 'seq', 'client')

    def __init__(self):
        self.quantity = None
        self.price = None
        self.side = None
        self.market = None
        self.contract = None
        self.accept_callback = None
        self.reject_callback = None
        self.invalid_callback = None
        self.seq = None
        self.client = None

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
        if self.quantity > 9223372036854775807L:
            raise ValueError("quantity cannot exceed 63 bits")

        if self.side not in (BUY, SELL):
            raise ValueError("side must be one of BUY or SELL")

        if not isinstance(self.market, seto.Uuid128):
            raise ValueError("market must be a valid seto.Uuid128")
        if not isinstance(self.contract, seto.Uuid128):
            raise ValueError("contract must be a valid seto.Uuid128")

    def copy_to(self, payload):
        "Copy this order instruction to a message `payload`"
        payload.type = seto.PAYLOAD_ORDER_CREATE
        payload.order_create.type = seto.ORDER_CREATE_LIMIT
        payload.order_create.market.CopyFrom(self.market)
        payload.order_create.contract.CopyFrom(self.contract)
        if self.side == BUY:
            payload.order_create.side = seto.SIDE_BUY
        elif self.side == SELL:
            payload.order_create.side = seto.SIDE_SELL
        payload.order_create.quantity_type = seto.QUANTITY_PAYOFF_CURRENCY
        payload.order_create.quantity = self.quantity
        payload.order_create.price_type = seto.PRICE_PERCENT_ODDS
        payload.order_create.price = self.price

    def register_callbacks(self, client):
        self.client = client
        if self.accept_callback is not None:
            client.add_handler('seto.order_accepted', self._accept_callback)
        if self.reject_callback is not None:
            client.add_handler('seto.order_rejected', self._reject_callback)
        if self.invalid_callback is not None:
            client.add_handler('seto.order_invalid', self._invalid_callback)

    def clear_callbacks(self):
        if self.accept_callback is not None:
            self.client.del_handler('seto.order_accepted', self._accept_callback)
        if self.reject_callback is not None:
            self.client.del_handler('seto.order_rejected', self._reject_callback)
        if self.invalid_callback is not None:
            self.client.del_handler('seto.order_invalid', self._invalid_callback)

    def _accept_callback(self, message):
        if message.order_accepted.seq == self.seq:
            self.accept_callback(message)
            self.clear_callbacks()

    def _reject_callback(self, message):
        if message.order_rejected.seq == self.seq:
            self.reject_callback(message)
            self.clear_callbacks()

    def _invalid_callback(self, message):
        if message.order_invalid.seq == self.seq:
            self.invalid_callback(message)
            self.clear_callbacks()

    def __repr__(self):
        return "OrderCreate(price=%r, quantity=%r, side=%r, market=%r, contract=%r)" % (
                    self.price, self.quantity, self.side, self.market, self.contract)


class OrderCancel(object):
    """ Message to cancel the specified order"""
    __slots__ = ('uid', 'seq')

    def __init__(self, uid=None):
        self.uid = uid

    def copy_to(self, payload):
        "Copy this instruction to a message `payload`"
        payload.type = seto.PAYLOAD_ORDER_CANCEL
        payload.order.CopyFrom(self.uid)
