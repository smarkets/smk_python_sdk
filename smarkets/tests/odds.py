from decimal import Decimal

from nose.tools.trivial import eq_

from smarkets.odds import Odds


def test_snap_to_decimal_buy():
    eq_(Decimal('18.87'), Odds.snap_to_decimal('buy', Decimal('18.6')).percent)


def test_snap_to_decimal_sell():
    eq_(Decimal('18.52'), Odds.snap_to_decimal('sell', Decimal('18.6')).percent)


def test_snap_to_decimal_move_out_by():
    eq_(Decimal('19.23'), Odds.snap_to_decimal_move_out_by('buy', Decimal('18.6'), 1).percent)


def test_snap_to_decimal_move_out_by_sell():
    eq_(Decimal('16.95'), Odds.snap_to_decimal_move_out_by('sell', Decimal('18.6'), 5).percent)


def test_snap_to_decimal_move_out_by_out_of_range():
    eq_(None, Odds.snap_to_decimal_move_out_by('sell', Decimal('18.6'), 5000))


def test_to_decimal_st():
    eq_(Odds.snap_to_decimal('sell', Decimal('5.13')).decimal_str, '19.5')
    eq_(Odds.snap_to_decimal('sell', Decimal('49.50')).decimal_str, '2.02')


def test_to_decimal_str_1_zero():
    eq_(Odds.snap_to_decimal('sell', Decimal('35.71')).decimal_str, '2.8')
    eq_(Odds.snap_to_decimal('sell', Decimal('6.25')).decimal_str, '16.0')


def test_to_decimal_str_2_zeros():
    eq_(Odds.snap_to_decimal('sell', Decimal('50')).decimal_str, '2.0')


def test_snap_to_decimal_buy_rounding():
    eq_(Decimal('45.05'), Odds.snap_to_decimal('buy', Decimal('45.045')).percent)


def test_snap_to_decimal_sell_rounding():
    eq_(Decimal('44.64'), Odds.snap_to_decimal('sell', Decimal('45.045')).percent)
