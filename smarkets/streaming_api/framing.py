from __future__ import absolute_import, division, print_function, unicode_literals

from six import indexbytes, int2byte


def frame_encode(payload):
    """
    :type payload: byte string
    :rtype: byte string
    """
    byte_count = len(payload)
    header = uleb128_encode(byte_count)

    # Minimum frame size is 4 bytes
    padding = b'\x00' * max(0, 4 - len(header) - len(payload))

    return header + payload + padding


def frame_decode_all(string):
    """
    :type string: byte string
    :rtype: tuple of (list of payloads) and remaining string
    """
    payloads = []
    frame_size = 4
    while len(string) >= frame_size:
        try:
            decoded = uleb128_decode(string)
        except IncompleteULEB128:
            # There may be not enough data in the input string to decode the header
            break
        else:
            payload_size, header_size = decoded
            frame_size = max(payload_size + header_size, 4)
            if len(string) >= frame_size:
                frame, string = string[:frame_size], string[frame_size:]
                payloads.append(frame[header_size:header_size + payload_size])

    return payloads, string


def uleb128_encode(value):
    """Encode a nonnegative int/long as a ULEB128 number.

    :type value: int or long
    :rtype: byte string
    """
    if value < 0:
        raise ValueError('Value needs to be nonnegative, got %r' % value)

    CONTINUATION_MARK = 0x80
    LEAST_MEANINGFUL_PART_MASK = 0x7f
    bits = value & LEAST_MEANINGFUL_PART_MASK
    value >>= 7
    ret = b''
    while value:
        ret += int2byte(CONTINUATION_MARK | bits)
        bits = value & LEAST_MEANINGFUL_PART_MASK
        value >>= 7
    return ret + int2byte(bits)


class IncompleteULEB128(Exception):
    pass


def uleb128_decode(string):
    """
    :type string: byte string
    :return: decoded value and number of bytes from the `string` used to decode it
    :rtype: tuple of (int or long) and int
    :raises:
        :IncompleteULEB128: when `string` doesn't start with ULEB128-encoded number.
    """
    CONTINUATION_MARK = 0x80
    LEAST_MEANINGFUL_PART_MASK = 0x7f

    shift = 0
    result = 0
    position = 0

    while True:
        try:
            current_byte = indexbytes(string, position)
        except IndexError:
            raise IncompleteULEB128('String does not start with a ULEB128-encoded value')
        else:
            result |= ((current_byte & LEAST_MEANINGFUL_PART_MASK) << shift)

            if not current_byte & CONTINUATION_MARK:
                break
            else:
                shift += 7
                position += 1

    return result, position + 1
