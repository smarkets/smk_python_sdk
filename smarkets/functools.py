from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ('overrides', 'OverrideError')


class OverrideError(Exception):
    '''Method override fails'''


def overrides(parent_class):
    '''Mark method as overriding parent_class' method.

    .. note::
        Overriding method can not have its own docstring.

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
        ...
        Traceback (most recent call last):
        OverrideError: No method 'methd' in class <class 'smarkets.functools.Parent'> to override
        >>>
        >>> class BadChild2(Parent):
        ...     @overrides(Parent)
        ...     def method(self):
        ...         'child method docstring'
        ...
        Traceback (most recent call last):
        OverrideError: No docstrings allowed in overriding method
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
            original = getattr(parent_class, name)
        except AttributeError:
            raise OverrideError('No method %r in class %r to override' % (name, parent_class))

        if fun.__doc__:
            raise OverrideError('No docstrings allowed in overriding method')

        fun.__doc__ = original.__doc__
        return fun

    return wrapper
