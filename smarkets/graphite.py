from __future__ import absolute_import, division, print_function, unicode_literals

import time
import socket


class Graphite(object):

    def __init__(self, host='localhost', port=2003, enabled=True, prefix=''):
        self.addr = None
        self.enabled = enabled
        if enabled:
            self.set_address(host, port)
        self.prefix = prefix
        self._socket = None

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
            self._connect()
            if self._socket is None:
                return
        if self.prefix:
            metric = "%s.%s" % (self.prefix, metric)
        try:
            self._socket.send("%s %s %s\n" % (metric, value, timestamp))
        except socket.error:
            self._socket = None


if __name__ == '__main__':
    graphite = Graphite()
    graphite.send_metric('test_client', 123)
