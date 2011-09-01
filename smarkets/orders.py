"Smarkets API client order objects"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php

import smarkets.seto.piqi_pb2 as seto


class Order(object):
    "Simple order state with useful exceptions"
    __slots__ = ('quantity', 'price', 'side', 'market', 'contract')

    BUY = 1
    SELL = 2

    def __init__(self):
        self.quantity = None
        self.price = None
        self.side = None
        self.market = None
        self.contract = None

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

        if self.side not in (self.BUY, self.SELL):
            raise ValueError("side must be one of BUY or SELL")

        if not isinstance(self.market, seto.Uuid128):
            raise ValueError("market must be a valid seto.Uuid128")
        if not isinstance(self.contract, seto.Uuid128):
            raise ValueError("contract must be a valid seto.Uuid128")

    def copy_to(self, payload, clear=True):
        "Copy this order instruction to a message `payload`"
        if clear:
            payload.Clear()
        payload.type = seto.PAYLOAD_ORDER_CREATE
        payload.order_create.type = seto.ORDER_CREATE_LIMIT
        payload.order_create.market.CopyFrom(self.market)
        payload.order_create.contract.CopyFrom(self.contract)
        if self.side == self.BUY:
            payload.order_create.side = seto.SIDE_BUY
        elif self.side == self.SELL:
            payload.order_create.side = seto.SIDE_SELL
        payload.order_create.quantity_type = seto.QUANTITY_PAYOFF_CURRENCY
        payload.order_create.quantity = self.quantity
        payload.order_create.price_type = seto.PRICE_PERCENT_ODDS
        payload.order_create.price = self.price
