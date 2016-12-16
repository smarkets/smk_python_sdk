from __future__ import absolute_import, division, print_function, unicode_literals

from six import int2byte


MIN_FRAME_SIZE = 4


class IncompleteULEB128(Exception):
    pass


def frame_encode(frame, payload):
    """
    Encodes payload and appends it to the given frame.
    :type frame: bytearray
    :type payload: byte string or bytearray
    """
    byte_count = len(payload)
    header = uleb128_encode(byte_count)
    padding = b'\x00' * max(0, MIN_FRAME_SIZE - len(header) - byte_count)
    frame += header
    frame += payload
    frame += padding


def uleb128_encode(value):
    """Encode a non-negative int/long as a ULEB128 number.

    :type value: int or long
    :rtype: bytearray
    """
    if value < 0:
        raise ValueError('Value needs to be non-negative, got %r' % value)

    CONTINUATION_MARK = 0x80
    LEAST_MEANINGFUL_PART_MASK = 0x7f
    bits = value & LEAST_MEANINGFUL_PART_MASK
    value >>= 7
    ret = bytearray()
    while value:
        ret += int2byte(CONTINUATION_MARK | bits)
        bits = value & LEAST_MEANINGFUL_PART_MASK
        value >>= 7
    ret += int2byte(bits)
    return ret


def frame_decode_all(to_decode):
    """
    :type to_decode: bytes
    :rtype: tuple (list of bytes, remaining bytes)
    """
    payloads = []
    while len(to_decode) >= MIN_FRAME_SIZE:
        try:
            decoded = uleb128_decode(to_decode)
        except IncompleteULEB128:
            # There may be not enough data in the input to decode the header
            break
        else:
            payload_size, header_size = decoded
            frame_size = max(payload_size + header_size, MIN_FRAME_SIZE)
            if len(to_decode) >= frame_size:
                frame, to_decode = to_decode[:frame_size], to_decode[frame_size:]
                payloads.append(frame[header_size:header_size + payload_size])
            else:
                break

    return payloads, to_decode


def uleb128_decode(to_decode):
    """
    :type to_decode: bytes
    :return: decoded value and number of bytes from `to_decode` used to decode it
    :rtype: tuple of (int or long) and int
    :raises:
        :IncompleteULEB128: when `to_decode` doesn't start with ULEB128-encoded number.
    """
    CONTINUATION_MARK = 0x80
    LEAST_MEANINGFUL_PART_MASK = 0x7f

    shift = 0
    result = 0
    position = 0

    while True:
        try:
            current_byte = to_decode[position]
        except IndexError:
            raise IncompleteULEB128('to_decode does not start with a ULEB128-encoded value')
        else:
            result |= ((current_byte & LEAST_MEANINGFUL_PART_MASK) << shift)

            if not current_byte & CONTINUATION_MARK:
                break
            else:
                shift += 7
                position += 1

    return result, position + 1
