from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import socket
import time

log = logging.getLogger(__name__)


class Graphite(object):

    def __init__(self, host='localhost', port=2003, enabled=True, prefix='', use_udp=False):
        self.addr = None
        self.enabled = enabled
        if enabled:
            self.set_address(host, port)
        self.prefix = prefix
        self._socket = None
        self._use_udp = use_udp

    def set_address(self, host, port):
        try:
            self.addr = (socket.gethostbyname(host), port)
        except socket.gaierror:
            self.addr = None
            self.enabled = False

    def _connect(self):
        try:
            self._socket = socket.create_connection(self.addr, 1)
        except socket.error:
            self.enabled = False
            self._socket = None

    def send_metric(self, metric, value, timestamp=None):
        if not self.enabled:
            return
        if timestamp is None:
            timestamp = time.time()
        if self._socket is None:
            if self._use_udp:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                self._connect()
                if self._socket is None:
                    return
        if self.prefix:
            metric = "%s.%s" % (self.prefix, metric)

        if self._use_udp:
            send_fun = lambda message: self._socket.sendto(message, self.addr)
        else:
            send_fun = self._socket.send

        try:
            message = "%s %s %s\n" % (metric, value, timestamp)
            send_fun(message)
        except socket.error as e:
            log.warn('Cannot send stuff to Graphite: %r', e)
            self._socket = None


if __name__ == '__main__':
    graphite = Graphite()
    graphite.send_metric('test_client', 123)
