from __future__ import absolute_import, division, print_function, unicode_literals

from smarkets.functools import deprecated_with_message
from smarkets.streaming_api import seto
from smarkets.string import camel_case_to_underscores

__all__ = ('int_to_uuid128', 'set_payload_message',)


def set_payload_message(payload, message):
    underscore_form = camel_case_to_underscores(type(message).__name__)
    payload_type = getattr(seto, 'PAYLOAD_' + underscore_form.upper())
    payload.type = payload_type
    getattr(payload, underscore_form).CopyFrom(message)


@deprecated_with_message('Using SETO UUID128 fields is deprecated now')
def int_to_uuid128(value):
    return seto.Uuid128(low=value)
