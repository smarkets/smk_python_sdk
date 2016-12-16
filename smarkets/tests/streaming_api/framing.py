from __future__ import absolute_import, division, print_function, unicode_literals

from itertools import chain

from nose.tools import eq_, raises
from six.moves import xrange

from smarkets.streaming_api.framing import (
    frame_decode_all, frame_encode, IncompleteULEB128, uleb128_decode, uleb128_encode,
)


test_data = (
    (0x00000000, b'\x00'),
    (0x0000007F, b'\x7F'),
    (0x00000080, b'\x80\x01'),
    (624485, b'\xE5\x8E\x26'),
    (268435202, b'\x82\xFE\xFF\x7F'),
)


def test_dumps():
    for value, string in test_data:
        yield check_dumps, value, string


def check_dumps(value, string):
    eq_(uleb128_encode(value), string)


def test_loads():
    for value, string in test_data:
        yield check_loads, bytearray(string), value


def check_loads(byte_array, value):
    eq_(uleb128_decode(byte_array), (value, len(byte_array)))


def test_loads_and_dumps_are_consistent():
    for i in chain(
        xrange(2 ** 18),
        xrange(2 ** 20, 2 ** 26, 33333),
        xrange(2 ** 26, 2 ** 32, 777777),
    ):
        byte_dump = uleb128_encode(i)
        eq_(uleb128_decode(byte_dump), (i, len(byte_dump)))


@raises(ValueError)
def test_uleb128_encode_fails_on_negative_number():
    uleb128_encode(-1)


def test_uleb128_decode_fails_on_invalid_input():
    byte_array = uleb128_encode(12345678)

    for i in xrange(len(byte_array)):
        yield check_uleb128_decode_fails_on_invalid_input, byte_array[:i]


@raises(IncompleteULEB128)
def check_uleb128_decode_fails_on_invalid_input(input_):
    uleb128_decode(input_)


def test_frame_encode():
    for input_, output in (
        (b'', b'\x00\x00\x00\x00'),
        (b'a', b'\x01a\x00\x00'),
        (b'ab', b'\x02ab\x00'),
        (b'abc', b'\x03abc'),
        (b'abcd', b'\x04abcd'),
    ):
        yield check_frame_encode, bytearray(input_), output


def check_frame_encode(byte_array, output):
    frame = bytearray()
    frame_encode(frame, byte_array)
    eq_(frame, output)


def test_frame_decode_all():
    for input_, output in (
        # frame matches the boundary
        (b'', ([], b'')),
        (b'\x01a\x00\x00\x02ab\x00\x03abc\x04abcd', ([b'a', b'ab', b'abc', b'abcd'], b'')),

        # ends with complete header but only part of a message
        (b'\x03ab', ([], b'\x03ab')),
        (b'\x01a\x00\x00\x02ab\x00\x03abc\x04abcd\x03ab', ([b'a', b'ab', b'abc', b'abcd'], b'\x03ab')),
        (b'\x05abcd', ([], b'\x05abcd')),

        # ends with incomplete header
        (b'\x80', ([], b'\x80')),
        (b'\x01a\x00\x00\x02ab\x00\x03abc\x04abcd\x03ab', ([b'a', b'ab', b'abc', b'abcd'], b'\x03ab')),

        # 4(or more)-byte incomplete header is a special case because it reaches the minimum frame size
        # so let's make sure decoding doesn't fail at header decoding stage
        (b'\x80\x80\x80\x80', ([], b'\x80\x80\x80\x80')),
        (b'\x80\x80\x80\x80\x80', ([], b'\x80\x80\x80\x80\x80')),

        # regression: if the second frame is shorter, we still want to decode both...
        (b'\x05abcde\x03abc', ([b'abcde', b'abc'], b'')),
    ):
        yield check_frame_decode_all, bytearray(input_), output


def check_frame_decode_all(byte_array, output):
    eq_(frame_decode_all(byte_array), output)
