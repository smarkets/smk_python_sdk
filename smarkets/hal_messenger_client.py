from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import socket

import simplejson as json

log = logging.getLogger(__name__)


def resolve_address_host(address):
    assert len(address) == 2, address
    return (socket.gethostbyname(address[0]), address[1])


class HalMessengerUDPClient(object):

    def __init__(self, address):
        """
        :type address: 2-tuple of string host (ip or domain) and integer port number
        """
        self._address = resolve_address_host(address)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message, room):
        payload = json.dumps(dict(message=message, room=room)).encode()
        bytes_sent = self._socket.sendto(payload, self._address)
        if bytes_sent != len(payload):
            log.warn('Sent %s bytes instead of %s. Payload: %s', bytes_sent, len(payload), payload)


class DummyHalMessengerClient(object):

    def send(self, message, room):
        pass
