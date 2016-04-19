from __future__ import absolute_import, division, print_function, unicode_literals

import json
import logging
import socket


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

    def send(self, raw_message, room, html_message=None, user=None):
        assert raw_message or html_message
        payload = json.dumps(dict(
            raw_message=raw_message,
            html_message=html_message,
            room=room,
            user=user,
        )).encode()
        bytes_sent = self._socket.sendto(payload, self._address)
        if bytes_sent != len(payload):
            log.warn('Sent %s bytes instead of %s. Payload: %s', bytes_sent, len(payload), payload)


class DummyHalMessengerClient(object):

    def send(self, raw_message, room, html_message=None, user=None):
        pass
