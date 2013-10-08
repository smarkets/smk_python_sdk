from __future__ import absolute_import

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


def namedtuple_asdict(nt):
    return OrderedDict(zip(nt._fields, nt))
