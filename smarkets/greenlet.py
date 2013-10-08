from __future__ import absolute_import

import gc
import traceback

import greenlet


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
