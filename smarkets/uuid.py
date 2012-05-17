"""
Utility methods for dealing with Smarkets UUIDS.

There are 3 main representations of IDs used in Smarkets:

- Integers (as in the API)
- Tagged UUIDs (used mostly on non-user-facing bits of the site)
- "Friendly" IDs/slugs (used on user-facing bits of the site)

"""
import types


_CHARS = '0123456789' \
    'abcdefghijklmnopqrstuvwxyz' \
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

_UUID_TAGS = {
    'Account':       'acc1',
    'ContractGroup': 'c024',
    'Contract':      'cccc',
    'Order':         'fff0',
    'Comment':       'b1a4',
    'Entity':        '0444',
    'Event':         '1100',
    'Session':       '9999',
    'User':          '0f00',
    'Referrer':      '4e4e'
}

_UUID_TAGS_BY_TAG = dict(((v, k) for k, v in _UUID_TAGS.iteritems()))
_UUID_INT_TAGS = dict((k, int(v, 16)) for k, v in _UUID_TAGS.iteritems())
_UUID_INT_TAGS_BY_TAG = dict((int(v, 16), k) for k, v in _UUID_TAGS.iteritems())


def _base_n(number, chars):
    """
    Helper method for recursing
    """
    return ((number == 0) and "0") \
        or (_base_n(number // (len(chars)), chars).lstrip("0") \
                + chars[number % (len(chars))])


def pad_uuid(uuid, pad=32, padchar='0'):
    "Pads a UUID with <pad> <padchar>s"
    return padchar * (pad - len(uuid)) + uuid


def int_to_slug(number, base=36, chars=_CHARS, prefix=None, pad=0):
    """
    Convert a large integer to a slug
    """
    if not isinstance(number, (int, long)):
        raise TypeError("Number must be an integer: %r" % number)
    if number < 0:
        raise TypeError("Number cannot be negative: %r" % number)
    if base < 2 or base > len(_CHARS):
        raise TypeError("base must be between 2 and %s" % len(_CHARS))
    chars = chars[:base]
    slug = pad_uuid(_base_n(number, chars), pad=pad)
    if prefix is not None:
        if not isinstance(prefix, types.StringTypes):
            raise TypeError("prefix must be a string: %r" % prefix)
        return '%s-%s' % (prefix, slug)
    return slug


def slug_to_int(slug, base=36, chars=_CHARS, prefix=None):
    """
    Convert a slug to a large integer
    """
    if not isinstance(slug, types.StringTypes):
        raise TypeError("slug must be a string: %r" % slug)
    if base < 2 or base > len(_CHARS):
        raise TypeError("base must be between 2 and %s" % len(_CHARS))
    if base <= 36:
        slug = slug.lower()
    chars = _CHARS[:base]
    index = dict(zip(chars, range(0, len(chars))))
    if prefix is not None:
        # Prefix is simply an assertion here
        got_prefix, slug = slug.split('-')
        if (prefix or got_prefix) != got_prefix:
            raise TypeError("Got prefix '%s' when expected '%s'" \
                                % (got_prefix, prefix))
    return reduce(lambda acc, val: acc + val[0] * len(index) ** val[1],
                  zip([index[x] for x in slug],
                      reversed(range(0, len(slug)))), 0)


def uuid_to_slug(number, base=36, chars=_CHARS, prefix=None, pad=0):
    """
    Convert a Smarkets UUID (128-bit hex) to a slug
    """
    if not isinstance(number, types.StringTypes):
        raise TypeError("Number must be a string: %r" % number)
    return int_to_slug(int(number, 16), base, chars, prefix, pad)


def slug_to_uuid(slug, base=36, chars=_CHARS, prefix=None, pad=32):
    """
    Convert a slug to a Smarkets UUID
    """
    if not isinstance(slug, types.StringTypes):
        raise TypeError("slug must be a string: %r" % slug)
    return pad_uuid('%x' % slug_to_int(slug, base, chars, prefix), pad=pad)


def int_to_uuid(number, type):
    "Convert an untagged integer into a tagged uuid"
    if not isinstance(number, (long, int)):
        raise TypeError("number must be an integer: %r", number)

    tag = _UUID_TAGS.get(type)
    if tag is None:
        raise ValueError("invalid type: %r" % type)

    return pad_uuid('%x%s' % (number, tag))


def uuid_to_int(uuid, return_tag=None):
    "Convert a tagged uuid into an integer, optionally returning type"
    tagless = uuid[:-4]
    number = int(tagless, 16)
    if return_tag == 'type':
        tag = uuid[-4:]
        tag_type = _UUID_TAGS_BY_TAG.get(tag)
        if tag_type is None:
            raise ValueError("Invalid tagged uuid: %r" % uuid)
        return (number, tag_type)
    if return_tag == 'int':
        return (number, int(uuid[-4:], 16))
    return number

def uuid_to_short(uuid):
    "Converts a full UUID to the shortened version"
    return uuid[:-4].lstrip('0')
