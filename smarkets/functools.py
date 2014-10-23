from __future__ import absolute_import, division, print_function, unicode_literals

import warnings
from collections import namedtuple
from functools import update_wrapper, wraps
from threading import RLock

from six import iteritems

__all__ = ('overrides', 'OverrideError', 'lru_cache', 'memoized')


class OverrideError(Exception):

    '''Method override fails'''


def overrides(ancestor_class):
    '''Mark method as overriding ``ancestor_class``' method.

    .. note::
        Overriding method can not have its own docstring.

    .. note::
        Method being overridden must be (re)defined in ``ancestor_class`` itself (see ``BadChild3``
        example below); :func:`overrides` will not follow the inheritance tree.

    Usage::

        >>> class Parent(object):
        ...     def method(self):
        ...         'parent docstring'
        ...
        >>>
        >>> class BadChild1(Parent):
        ...     @overrides(Parent)
        ...     def methd(self):
        ...         pass
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        ...
        Traceback (most recent call last):
        OverrideError: No method 'methd' in class <class 'smarkets.functools.Parent'> to override
        >>>
        >>> class BadChild2(Parent):
        ...     @overrides(Parent)
        ...     def method(self):
        ...         'child method docstring'
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        ...
        Traceback (most recent call last):
        OverrideError: No docstrings allowed in overriding method
        >>>
        >>> class IntermediateChild(Parent):
        ...     pass
        ...
        >>> class BadChild3(IntermediateChild):
        ...     @overrides(IntermediateChild)
        ...     def method(self):
        ...         pass
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        ...
        Traceback (most recent call last):
        OverrideError: No method 'method' in class <class 'smarkets.functools.IntermediateChild'> to override
        >>>
        >>> class GoodChild(Parent):
        ...     @overrides(Parent)
        ...     def method(self):
        ...         return 1
        ...
        >>> child = GoodChild()
        >>> str(child.method.__doc__)
        'parent docstring'
        >>> child.method()
        1

    :raises:
        :OverrideError: Method does not exist in parent class or overriding method has docstring.
    '''
    def wrapper(fun):
        name = fun.__name__
        try:
            original = ancestor_class.__dict__[name]
        except KeyError:
            raise OverrideError('No method %r in class %r to override' % (name, ancestor_class))

        if fun.__doc__:
            raise OverrideError('No docstrings allowed in overriding method')

        fun.__doc__ = original.__doc__
        return fun

    return wrapper


# The lru_cache decorator is a backport from python 3.3, found here:
# http://code.activestate.com/recipes/578078-py26-and-py30-backport-of-python-33s-lru-cache/

_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])


class _HashedSeq(list):
    __slots__ = 'hashvalue'

    def __init__(self, tup, hash=hash):
        self[:] = tup
        self.hashvalue = hash(tup)

    def __hash__(self):
        return self.hashvalue


def _make_key(args, kwds, typed,
              kwd_mark=(object(),),
              fasttypes=set([int, str, frozenset, type(None)]),
              sorted=sorted, tuple=tuple, type=type, len=len):
    'Make a cache key from optionally typed positional and keyword arguments'
    key = args
    if kwds:
        sorted_items = sorted(kwds.items())
        key += kwd_mark
        for item in sorted_items:
            key += item
    if typed:
        key += tuple(type(v) for v in args)
        if kwds:
            key += tuple(type(v) for k, v in sorted_items)
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedSeq(key)


def lru_cache(maxsize=100, typed=False):
    """Least-recently-used cache decorator.

    If *maxsize* is set to None, the LRU features are disabled and the cache
    can grow without bound.

    If *typed* is True, arguments of different types will be cached separately.
    For example, f(3.0) and f(3) will be treated as distinct calls with
    distinct results.

    Arguments to the cached function must be hashable.

    View the cache statistics named tuple (hits, misses, maxsize, currsize) with
    f.cache_info().  Clear the cache and statistics with f.cache_clear().
    Access the underlying function with f.__wrapped__.

    See:  http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

    """

    # Users should only access the lru_cache through its public API:
    #       cache_info, cache_clear, and f.__wrapped__
    # The internals of the lru_cache are encapsulated for thread safety and
    # to allow the implementation to change (including a possible C version).

    def decorating_function(user_function):

        cache = dict()
        stats = [0, 0]                  # make statistics updateable non-locally
        HITS, MISSES = 0, 1             # names for the stats fields
        make_key = _make_key
        cache_get = cache.get           # bound method to lookup key or return None
        _len = len                      # localize the global len() function
        lock = RLock()                  # because linkedlist updates aren't threadsafe
        root = []                       # root of the circular doubly linked list
        root[:] = [root, root, None, None]      # initialize by pointing to self
        nonlocal_root = [root]                  # make updateable non-locally
        PREV, NEXT, KEY, RESULT = 0, 1, 2, 3    # names for the link fields

        if maxsize == 0:

            def wrapper(*args, **kwds):
                # no caching, just do a statistics update after a successful call
                result = user_function(*args, **kwds)
                stats[MISSES] += 1
                return result

        elif maxsize is None:

            def wrapper(*args, **kwds):
                # simple caching without ordering or size limit
                key = make_key(args, kwds, typed)
                result = cache_get(key, root)   # root used here as a unique not-found sentinel
                if result is not root:
                    stats[HITS] += 1
                    return result
                result = user_function(*args, **kwds)
                cache[key] = result
                stats[MISSES] += 1
                return result

        else:

            def wrapper(*args, **kwds):
                # size limited caching that tracks accesses by recency
                key = make_key(args, kwds, typed) if kwds or typed else args
                with lock:
                    link = cache_get(key)
                    if link is not None:
                        # record recent use of the key by moving it to the front of the list
                        root, = nonlocal_root
                        link_prev, link_next, key, result = link
                        link_prev[NEXT] = link_next
                        link_next[PREV] = link_prev
                        last = root[PREV]
                        last[NEXT] = root[PREV] = link
                        link[PREV] = last
                        link[NEXT] = root
                        stats[HITS] += 1
                        return result
                result = user_function(*args, **kwds)
                with lock:
                    root, = nonlocal_root
                    if key in cache:
                        # getting here means that this same key was added to the
                        # cache while the lock was released.  since the link
                        # update is already done, we need only return the
                        # computed result and update the count of misses.
                        pass
                    elif _len(cache) >= maxsize:
                        # use the old root to store the new key and result
                        oldroot = root
                        oldroot[KEY] = key
                        oldroot[RESULT] = result
                        # empty the oldest link and make it the new root
                        root = nonlocal_root[0] = oldroot[NEXT]
                        oldkey = root[KEY]
                        root[KEY] = root[RESULT] = None
                        # now update the cache dictionary for the new links
                        del cache[oldkey]
                        cache[key] = oldroot
                    else:
                        # put result in a new link at the front of the list
                        last = root[PREV]
                        link = [last, root, key, result]
                        last[NEXT] = root[PREV] = cache[key] = link
                    stats[MISSES] += 1
                return result

        def cache_info():
            """Report cache statistics"""
            with lock:
                return _CacheInfo(stats[HITS], stats[MISSES], maxsize, len(cache))

        def cache_clear():
            """Clear the cache and cache statistics"""
            with lock:
                cache.clear()
                root = nonlocal_root[0]
                root[:] = [root, root, None, None]
                stats[:] = [0, 0]

        wrapper.__wrapped__ = user_function
        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return update_wrapper(wrapper, user_function)

    return decorating_function


def deprecated_with_message(message):
    def decorator_(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                ('Function %r is deprecated. %s') % (func.__name__, message),
                DeprecationWarning, stacklevel=3)
            return func(*args, **kwargs)
        return wrapper
    return decorator_


def memoized(fun):
    storage = {}

    @wraps(fun)
    def wrapper(*args, **kwargs):
        key = (args, tuple(iteritems(kwargs)))
        try:
            value = storage[key]
        except KeyError:
            value = storage[key] = fun(*args, **kwargs)
        return value
    return wrapper


def always_return(value):
    def fun(*args, **kwargs):
        return value
    return fun
