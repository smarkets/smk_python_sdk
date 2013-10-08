from __future__ import absolute_import, division, print_function, unicode_literals

from itertools import islice

from six import exec_, iteritems


try:
    exec_('''
    def mapkeys(function, mapping):
        return {function(k): v for (k, v) in iteritems(mapping)}

    def mapvalues(function, mapping):
        return {k: function(v) for (k, v) in iteritems(mapping)}
    ''')

except SyntaxError:
    def mapkeys(function, mapping):
        return dict((function(k), v) for (k, v) in iteritems(mapping))

    def mapvalues(function, mapping):
        return dict((k, function(v)) for (k, v) in iteritems(mapping))


def group(iterable, n):
    iterator = iter(iterable)
    chunk = True
    while chunk:
        chunk = tuple(islice(iterator, n))
        if chunk:
            yield chunk
