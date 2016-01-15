from __future__ import absolute_import

"""
Utility methods for dealing with Smarkets UUIDS.

There are 3 main representations of IDs used in Smarkets:

- Integers (as in the API)
- Tagged UUIDs (used mostly on non-user-facing bits of the site)
- "Friendly" IDs/slugs (used on user-facing bits of the site)

"""
import logging
from collections import namedtuple

from six import binary_type, integer_types, string_types
from six.moves import reduce

log = logging.getLogger(__name__)


UuidTagBase = namedtuple('UuidTagBase', ['name', 'int_tag', 'prefix'])
UuidBase = namedtuple('UuidBase', ['number', 'tag'])


class UuidTag(UuidTagBase):  # pylint: disable=E1001

    "Represents tag information"
    __slots__ = ()
    tag_mult = 1 << 16

    @property
    def hex_str(self):
        "Hex tag value"
        return '%04x' % self.int_tag

    def tag_number(self, number):
        "Adds this tag to a number"
        return number * self.tag_mult + self.int_tag

    @classmethod
    def split_int_tag(cls, number):
        "Splits a number into the ID and tag"
        return divmod(number, cls.tag_mult)

TAGS = (
    UuidTag('Account', int('acc1', 16), 'a'),
    UuidTag('ContractGroup', int('c024', 16), 'm'),
    UuidTag('Contract', int('cccc', 16), 'c'),
    UuidTag('Order', int('fff0', 16), 'o'),
    UuidTag('Comment', int('b1a4', 16), 'b'),
    UuidTag('Entity', int('0444', 16), 'n'),
    UuidTag('Event', int('1100', 16), 'e'),
    UuidTag('Session', int('9999', 16), 's'),
    UuidTag('User', int('0f00', 16), 'u'),
    UuidTag('Referrer', int('4e4e', 16), 'r'),
)


class Uuid(UuidBase):  # pylint: disable=E1001

    "Represents a UUID"
    __slots__ = ()
    chars = (
        '0123456789'
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    )

    # Various indexes into uuid map
    tags = dict((t.name, t) for t in TAGS)
    tags_by_hex_str = dict((t.hex_str, t) for t in TAGS)
    tags_by_prefix = dict((t.prefix, t) for t in TAGS)
    tags_by_int_tag = dict((t.int_tag, t) for t in TAGS)
    mask64 = (1 << 64) - 1

    @property
    def low(self):
        "Lower 64 bits of number"
        return self.number & self.mask64

    @property
    def high(self):
        "Higher 64 bits of number"
        return (self.number >> 64) & self.mask64

    @property
    def shorthex(self):
        "Short hex representation of Uuid"
        return '%x' % self.number

    def to_slug(self, prefix=True, base=36, chars=None, pad=0):
        "Convert to slug representation"
        if chars is None:
            chars = self.chars
        if base < 2 or base > len(chars):
            raise TypeError("base must be between 2 and %s" % len(chars))
        chars = chars[:base]
        number = self.tag.tag_number(self.number)
        slug = self.pad_uuid(self.base_n(number, chars), pad=pad)
        if prefix:
            return '%s-%s' % (self.tag.prefix, slug)
        else:
            return slug

    def to_hex(self, pad=32):
        "Convert to tagged hex representation"
        hex_str = '%x%s' % (self.number, self.tag.hex_str)
        return self.pad_uuid(hex_str, pad=pad)

    @staticmethod
    def base_n(number, chars):
        "Recursive helper for calculating a number in base len(chars)"
        return ((number == 0) and "0") \
            or (Uuid.base_n(number // (len(chars)), chars).lstrip("0") +
                chars[number % (len(chars))])

    @staticmethod
    def pad_uuid(uuid, pad=32, padchar='0'):
        "Pads a UUID with <pad> <padchar>s"
        return padchar * (pad - len(uuid)) + uuid

    @classmethod
    def unsplit64(cls, high, low):
        "Converts a high/low 64-bit integer pair into a 128-bit large integer"
        return ((high & cls.mask64) << 64) | (low & cls.mask64)

    @classmethod
    def from_int(cls, number, ttype):
        "Convert an integer and tag type to a Uuid"
        if isinstance(number, tuple):
            number = cls.unsplit64(*number)
        if not isinstance(number, integer_types):
            raise TypeError("Number must be an integer: %r" % number)
        if number < 0:
            raise TypeError("Number cannot be negative: %r" % number)
        tag = cls.tags.get(ttype)
        if tag is None:
            raise ValueError("invalid type: %r" % ttype)
        return cls(number, tag)

    @classmethod
    def from_slug(cls, slug, base=36, chars=None):
        "Convert a slug into a Uuid"
        if not isinstance(slug, string_types):
            raise TypeError("slug must be a string: %r" % slug)
        if chars is None:
            chars = cls.chars
        if base < 2 or base > len(chars):
            raise TypeError("base must be between 2 and %s" % len(chars))
        if base <= 36:
            slug = slug.lower()
        chars = chars[:base]
        index = dict(zip(chars, range(0, len(chars))))
        prefix = None
        if len(slug) > 1 and '-' in slug:
            # We have a prefix
            prefix, slug = slug.split('-')
        number = reduce(lambda acc, val: acc + val[0] * len(index) ** val[1],
                        zip([index[x] for x in slug],
                            reversed(range(0, len(slug)))), 0)
        number, int_tag = UuidTag.split_int_tag(number)
        tag = cls.tags_by_int_tag.get(int_tag)
        if tag is None:
            raise ValueError("invalid integer tag: %r" % int_tag)
        if prefix and tag != cls.tags_by_prefix.get(prefix):
            raise ValueError("prefix %r did not match tag %r" % (prefix, tag))
        return cls(number, tag)

    @classmethod
    def from_hex(cls, hex_str):
        """Convert a hex uuid into a Uuid
        :type hex_str: byte string or unicode string
        """
        if isinstance(hex_str, binary_type):
            hex_str = hex_str.decode()
        if not isinstance(hex_str, string_types):
            raise TypeError("hex_str must be a string: %r" % hex_str)
        hex_tag = hex_str[-4:]
        number = int(hex_str[:-4], 16)
        tag = cls.tags_by_hex_str.get(hex_tag)
        if tag is None:
            raise ValueError("invalid hex tag: %r" % hex_tag)
        return cls(number, tag)


def int_to_slug(number, ttype):
    "Convert a large integer to a slug"
    return Uuid.from_int(number, ttype).to_slug()


def slug_to_int(slug, return_tag=None, split=False):
    """
    Convert a slug to an integer, optionally splitting into high and
    low 64 bit parts
    """
    uuid = Uuid.from_slug(slug)
    number = (uuid.high, uuid.low) if split else uuid.number
    if return_tag == 'type':
        return (number, uuid.tag.name)
    elif return_tag == 'int':
        return (number, uuid.tag.int_tag)
    else:
        return number


def uuid_to_slug(number, prefix=True):
    """
    Convert a Smarkets UUID (128-bit hex) to a slug
    """
    return Uuid.from_hex(number).to_slug(prefix=prefix)


def slug_to_uuid(slug):
    """
    Convert a slug to a Smarkets UUID
    """
    return Uuid.from_slug(slug).to_hex()


def int_to_uuid(number, ttype):
    """Convert an untagged integer into a tagged uuid

    :type ttype: str or unicode on Python 2, str on Python 3
    """
    return Uuid.from_int(number, ttype).to_hex()


def uuid_to_int(uuid, return_tag=None, split=False):
    "Convert a tagged uuid into an integer, optionally returning type"
    uuid = Uuid.from_hex(uuid)
    number = (uuid.high, uuid.low) if split else uuid.number
    if return_tag == 'type':
        return (number, uuid.tag.name)
    elif return_tag == 'int':
        return (number, uuid.tag.int_tag)
    else:
        return number


def uid_or_int_to_int(value, expected_type):
    if not isinstance(value, integer_types):
        value, type_ = uuid_to_int(value, return_tag='type')
        if type_ != expected_type:
            raise ValueError("Expected tag %r doesn't match %r" % (expected_type, type_))

    return value


contract_group_id_to_uid = lambda id_: int_to_uuid(id_, 'ContractGroup')
contract_id_to_uid = lambda id_: int_to_uuid(id_, 'Contract')
event_id_to_uid = lambda id_: int_to_uuid(id_, 'Event')
order_id_to_uid = lambda id_: int_to_uuid(id_, 'Order')
account_id_to_uid = lambda id_: int_to_uuid(id_, 'Account')
entity_id_to_uid = lambda id_: int_to_uuid(id_, 'Entity')
user_id_to_uid = lambda id_: int_to_uuid(id_, 'User')
session_id_to_uid = lambda id_: int_to_uuid(id_, 'Session')


def uuid_to_short(uuid):
    "Converts a full UUID to the shortened version"
    return uuid[:-4].lstrip('0')
