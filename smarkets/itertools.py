from __future__ import absolute_import, division, print_function, unicode_literals

from itertools import islice

from six import exec_, iteritems, iterkeys, itervalues

__all__ = ['listitems', 'listkeys', 'listvalues', 'mapkeys', 'mapvalues', ]

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


def listkeys(d):
    """Return `d` key list"""
    return list(iterkeys(d))


def listvalues(d):
    """Return `d` value list"""
    return list(itervalues(d))


def listitems(d):
    """Return `d` item list"""
    return list(iteritems(d))


def inverse_mapping(d):
    """Return a dictionary with input mapping keys as values and values as keys.

    :raises:
        :ValueError: Input mapping values aren't uniqe.
    """

    new_mapping = {v: k for k, v in iteritems(d)}
    if len(new_mapping) != len(d):
        raise ValueError("Input mapping values aren't unique")
    return new_mapping


def is_sorted(sequence, **kwargs):
    """
    :type sequence: tuple or list
    :param kwargs: :func:`sorted` kwargs
    """
    if not isinstance(sequence, (tuple, list)):
        raise TypeError('Sequence needs to be a tuple or a list')

    if not isinstance(sequence, list):
        sequence = list(sequence)

    return sorted(sequence, **kwargs) == sequence


def has_unique_elements(sequence):
    return len(set(sequence)) == len(sequence)
