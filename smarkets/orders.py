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
                 'accept_callback', 'reject_callback', 'invalid_callback', 'executed_callback',
                 'seq', 'client', 'time_in_force')

    def __init__(self):
        self.quantity = None
        self.price = None
        self.side = None
        self.market = None
        self.contract = None
        self.accept_callback = None
        self.reject_callback = None
        self.invalid_callback = None
        self.executed_callback = None
        self.seq = None
        self.client = None
        self.time_in_force = None

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

        if self.time_in_force:
            if not self.time_in_force == seto.IMMEDIATE_OR_CANCEL and \
               not self.time_in_force == seto.GOOD_TIL_CANCELLED:
                raise ValueError("Time inforce must be one of IMMEDIATE_OR_CANCEL, GOOD_TIL_CANCELLED")

    def copy_to(self, payload):
        "Copy this order instruction to a message `payload`"
        payload.type = seto.PAYLOAD_ORDER_CREATE
        payload.order_create.type = seto.ORDER_CREATE_LIMIT
        payload.order_create.tif = seto.IMMEDIATE_OR_CANCEL
        payload.order_create.market.CopyFrom(self.market)
        payload.order_create.contract.CopyFrom(self.contract)
        if self.time_in_force:
            payload.order_create.tif = self.time_in_force
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
        if self.executed_callback is not None:
            client.add_handler('seto.order_executed', self._executed_callback)

    def clear_callbacks(self):
        self.clear_acceptance_callbacks()
        self.clear_execution_callbacks()

    def clear_acceptance_callbacks(self):
        if self.accept_callback is not None:
            self.client.del_handler('seto.order_accepted', self._accept_callback)
        if self.reject_callback is not None:
            self.client.del_handler('seto.order_rejected', self._reject_callback)
        if self.invalid_callback is not None:
            self.client.del_handler('seto.order_invalid', self._invalid_callback)

    def clear_execution_callbacks(self):
        if self.executed_callback is not None:
            self.client.del_handler('seto.order_executed', self._executed_callback)

    def _accept_callback(self, message):
        if message.order_accepted.seq == self.seq:
            self.clear_acceptance_callbacks()
            self.accept_callback(message)

    def _reject_callback(self, message):
        if message.order_rejected.seq == self.seq:
            self.clear_callbacks()
            self.reject_callback(message)

    def _invalid_callback(self, message):
        if message.order_invalid.seq == self.seq:
            self.clear_callbacks()
            self.invalid_callback(message)

    def _executed_callback(self, message):
        self.clear_execution_callbacks()
        self.executed_callback(message)

    def __repr__(self):
        return "OrderCreate(price=%r, quantity=%r, side=%r, market=%r, contract=%r)" % (
            self.price, self.quantity, self.side, self.market, self.contract)


class OrderCancel(object):

    """ Message to cancel the specified order"""
    __slots__ = ('uid', 'seq', 'client', 'cancelled_callback', 'reject_callback')

    def __init__(self, uid=None):
        self.uid = uid
        self.client = None
        self.cancelled_callback = None
        self.reject_callback = None

    def validate_new(self):
        "Validate this order's properties as a new instruction"
        if not isinstance(self.uid, seto.Uuid128):
            raise ValueError("order uid must be a valid seto.Uuid128")

    def copy_to(self, payload):
        "Copy this instruction to a message `payload`"
        payload.type = seto.PAYLOAD_ORDER_CANCEL
        payload.order_cancel.order.CopyFrom(self.uid)

    def register_callbacks(self, client):
        self.client = client
        if self.cancelled_callback is not None:
            client.add_handler('seto.order_cancelled', self._cancelled_callback)
        if self.reject_callback is not None:
            client.add_handler('seto.order_cancel_rejected', self._reject_callback)

    def clear_callbacks(self):
        if self.cancelled_callback is not None:
            self.client.del_handler('seto.order_cancelled', self._cancelled_callback)
        if self.reject_callback is not None:
            self.client.del_handler('seto.order_cancel_rejected', self._reject_callback)

    def _cancelled_callback(self, message):
        self.clear_callbacks()
        self.cancelled_callback(message)

    def _reject_callback(self, message):
        if message.order_cancel_rejected.seq == self.seq:
            self.clear_callbacks()
            self.reject_callback(message)


class OrdersForMarket(object):

    """ Message to cancel the specified order"""
    __slots__ = ('market_uid', 'seq')

    def __init__(self, market_uid):
        self.market_uid = market_uid

    def validate_new(self):
        if not isinstance(self.market_uid, seto.Uuid128):
            raise ValueError("market must be a valid seto.Uuid128")

    def copy_to(self, payload):
        "Copy this instruction to a message `payload`"
        payload.type = seto.PAYLOAD_ORDERS_FOR_MARKET_REQUEST
        payload.orders_for_market_request.market.CopyFrom(self.market_uid)
