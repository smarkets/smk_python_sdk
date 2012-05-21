"""
Utility methods for dealing with Smarkets UUIDS.

There are 3 main representations of IDs used in Smarkets:

- Integers (as in the API)
- Tagged UUIDs (used mostly on non-user-facing bits of the site)
- "Friendly" IDs/slugs (used on user-facing bits of the site)

"""
import types

from collections import namedtuple


UuidTagBase = namedtuple('UuidTag', ['name', 'hex_str', 'prefix'])
UuidBase = namedtuple('Uuid', ['number', 'tag'])


class UuidTag(UuidTagBase):
    "Represents tag information"
    tag_mult = 1 << 16
    @property
    def int_tag(self):
        return int(self.hex_str, 16)

    def tag_number(self, number):
        "Adds this tag to a number"
        return number * self.tag_mult + self.int_tag

    @classmethod
    def split_int_tag(cls, number):
        "Splits a number into the ID and tag"
        return divmod(number, cls.tag_mult)


class Uuid(UuidBase):
    "Represents a UUID"
    chars = '0123456789' \
        'abcdefghijklmnopqrstuvwxyz' \
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    tag_list = (
        UuidTag('Account',       'acc1', 'a'),
        UuidTag('ContractGroup', 'c024', 'm'),
        UuidTag('Contract',      'cccc', 'c'),
        UuidTag('Order',         'fff0', 'o'),
        UuidTag('Comment',       'b1a4', 'b'),
        UuidTag('Entity',        '0444', 'n'),
        UuidTag('Event',         '1100', 'e'),
        UuidTag('Session',       '9999', 's'),
        UuidTag('User',          '0f00', 'u'),
        UuidTag('Referrer',      '4e4e', 'r'),
    )

    # Various indexes into uuid map
    tags = dict((t.name, t) for t in tag_list)
    tags_by_hex_str = dict((t.hex_str, t) for t in tag_list)
    tags_by_prefix = dict((t.prefix, t) for t in tag_list)
    tags_by_int_tag = dict((t.int_tag, t) for t in tag_list)
    mask64 = (1 << 64) - 1

    @property
    def low(self):
        return self.number & self.mask64

    @property
    def high(self):
        return (self.number >> 64) & self.mask64

    @property
    def shorthex(self):
        return '%x' % self.number

    def to_slug(self, base=36, chars=None, pad=0):
        if chars is None:
            chars = self.chars
        if base < 2 or base > len(chars):
            raise TypeError("base must be between 2 and %s" % len(chars))
        chars = chars[:base]
        number = self.tag.tag_number(self.number)
        slug = self.pad_uuid(self.base_n(number, chars), pad=pad)
        return '%s-%s' % (self.tag.prefix, slug)

    def to_hex(self, pad):
        hex_str = '%x%s' % (self.number, self.tag.hex_str)
        return self.pad_uuid(hex_str, pad=pad)

    @staticmethod
    def base_n(number, chars):
        return ((number == 0) and "0") \
            or (Uuid.base_n(number // (len(chars)), chars).lstrip("0") \
                    + chars[number % (len(chars))])

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
        if not isinstance(number, (int, long)):
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
        if not isinstance(slug, types.StringTypes):
            raise TypeError("slug must be a string: %r" % slug)
        if chars is None:
            chars = cls.chars
        if base < 2 or base > len(chars):
            raise TypeError("base must be between 2 and %s" % len(chars))
        if base <= 36:
            slug = slug.lower()
        chars = chars[:base]
        index = dict(zip(chars, range(0, len(chars))))
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
        return cls(number, tag)

    @classmethod
    def from_hex(cls, hex_str):
        "Convert a hex uuid into a Uuid"
        if not isinstance(hex_str, types.StringTypes):
            raise TypeError("hexstr must be a string: %r" % hexstr)
        hex_tag = hex_str[-4:]
        number = int(hex_str[:-4], 16)
        tag = cls.tags_by_hex_str.get(hex_tag)
        if tag is None:
            raise ValueError("invalid hex tag: %r" % hex_tag)
        return cls(number, tag)


def int_to_slug(number, ttype, base=36, chars=None, pad=0):
    "Convert a large integer to a slug"
    return Uuid.from_int(number, ttype).to_slug(base, chars, pad)


def slug_to_int(slug, base=36, chars=None, split=True, return_type=False):
    """
    Convert a slug to an integer, optionally splitting into high and
    low 64 bit parts
    """
    uuid = Uuid.from_slug(slug, base, chars)
    number = (uuid.high, uuid.low) if split else uuid.number
    return (number, uuid.tag.name) if return_type else number


def uuid_to_slug(number, base=36, chars=None, pad=0):
    """
    Convert a Smarkets UUID (128-bit hex) to a slug
    """
    return Uuid.from_hex(number).to_slug(base, chars, pad)


def slug_to_uuid(slug, base=36, chars=None, pad=32):
    """
    Convert a slug to a Smarkets UUID
    """
    return Uuid.from_slug(slug, base, chars).to_hex(pad)


def int_to_uuid(number, ttype, pad=32):
    "Convert an untagged integer into a tagged uuid"
    return Uuid.from_int(number, ttype).to_hex(pad)


def uuid_to_int(uuid, return_tag=None, split=False):
    "Convert a tagged uuid into an integer, optionally returning type"
    uuid = Uuid.from_hex(uuid)
    number = (uuid.high, uuid.low) if split else uuid.number
    if return_tag == 'type':
        return (number, uuid.tag.name)
    if return_tag == 'int':
        return (number, uuid.tag.int_tag)
    return number


def uuid_to_short(uuid):
    "Converts a full UUID to the shortened version"
    return uuid[:-4].lstrip('0')
