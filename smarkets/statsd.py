from __future__ import absolute_import, division, print_function, unicode_literals

# Statsd client. Loosely based on the version by Steve Ivy <steveivy@gmail.com>

import logging
import random
import socket
import time
from contextlib import contextmanager

log = logging.getLogger(__name__)


class StatsD(object):

    def __init__(self, host='localhost', port=8125, enabled=True, prefix=''):
        self.addr = None
        self.enabled = enabled
        if enabled:
            self.set_address(host, port)
        self.prefix = prefix
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def set_address(self, host, port=8125):
        try:
            self.addr = (socket.gethostbyname(host), port)
        except socket.gaierror:
            self.addr = None
            self.enabled = False

    @contextmanager
    def timed(self, stat, sample_rate=1):
        log.debug('Entering timed context for %r' % (stat,))
        start = time.time()
        yield
        duration = int((time.time() - start) * 1000)
        log.debug('Exiting timed context for %r' % (stat,))
        self.timing(stat, duration, sample_rate)

    def timing(self, stats, time, sample_rate=1):
        """
        Log timing information
        """
        unit = 'ms'
        log.debug('%r took %s %s' % (stats, time, unit))
        self.update_stats(stats, "%s|%s" % (time, unit), sample_rate)

    def increment(self, stats, sample_rate=1):
        """
        Increments one or more stats counters
        """
        self.update_stats(stats, 1, sample_rate)

    def decrement(self, stats, sample_rate=1):
        """
        Decrements one or more stats counters
        """
        self.update_stats(stats, -1, sample_rate)

    def update_stats(self, stats, delta=1, sampleRate=1):
        """
        Updates one or more stats counters by arbitrary amounts
        """
        if not self.enabled or self.addr is None:
            return

        if type(stats) is not list:
            stats = [stats]
        data = {}
        for stat in stats:
            data["%s%s" % (self.prefix, stat)] = "%s|c" % delta

        self.send(data, sampleRate)

    def send(self, data, sample_rate):
        sampled_data = {}

        if sample_rate < 1:
            if random.random() <= sample_rate:
                for stat, value in data.items():
                    sampled_data[stat] = "%s|@%s" % (value, sample_rate)
        else:
            sampled_data = data

        try:
            for stat, value in sampled_data.items():
                self.udp_sock.sendto("%s:%s" % (stat, value), self.addr)
        except Exception as e:
            log.exception('Failed to send data to the server: %r', e)


if __name__ == '__main__':
    sd = StatsD()
    for i in range(1, 100):
        sd.increment('test')
