from __future__ import absolute_import

import gc
import traceback

try:
    from eventlet import sleep
except ImportError:
    def sleep():
        raise NotImplementedError('Eventlet not found')

import greenlet

__all__ = (
    'get_greenlet_stack_trace', 'get_all_greenlets', 'get_process_debug_info', 'cooperative_iter',
)


def get_greenlet_stack_trace(g):
    '''
    Gets formatted stack trace for greenlet g;
    :type g: greenlet.greenlet
    :rtype: unicode
    '''
    stack = traceback.format_stack(g.gr_frame)
    return ''.join(stack)


def get_all_greenlets():
    '''
    Gets all allocated greenlets.
    :rtype: set of greenlet.greenlet
    '''
    return set(obj for obj in gc.get_objects() if isinstance(obj, greenlet.greenlet))


def get_process_debug_info():
    '''
    Gets some process debug information.
    :rtype: iterable of debug messages
    '''
    current = greenlet.getcurrent()
    greenlets = get_all_greenlets()
    messages = [
        "Current greenlet is %s. Stack trace:\n%s" % (current, get_greenlet_stack_trace(current),),
        "Number of greenlets: %d\n" % (len(greenlets),),
    ]

    messages.extend('Greenlet %s stack trace:\n%s' % (g, get_greenlet_stack_trace(g))
                    for g in greenlets if g is not current)
    return messages


def cooperative_iter(iterable, chunk_size=1, interval=0):
    """
    Returns an iterator which wraps `iterable` and sleeps `interval` every `chunk_size`
    elements. This makes iterating `iterable` more green and can prevent starving other
    greenlets/greenthreads.

    :type iterable: iterable
    :type chunk_size: int
    :type interval: float
    """

    for index, element in enumerate(iterable):
        yield element
        if index % chunk_size == 0:
            sleep(interval)


def cooperative_yield(secs=0):
    """Yield to Eventlet hub for `secs` seconds.

    This is equivalent to calling eventlet.sleep(secs) but better express the semantics.
    """
    sleep(secs)
