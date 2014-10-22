from nose.tools import eq_, raises

from smarkets.itertools import (
    copy_keys_if_present,
    group,
    has_unique_elements,
    inverse_mapping,
    is_sorted,
    listitems,
    listkeys,
    listmap,
    listvalues,
    mapkeys,
    mapvalues,
)


def test_mapkeys():
    eq_(mapkeys(str, {1: 'this', 2: 'that'}),
        {'1': 'this', '2': 'that'})


def test_mapvalues():
    eq_(mapvalues(tuple, {1: 'this', 2: 'that'}),
        {1: ('t', 'h', 'i', 's',), 2: ('t', 'h', 'a', 't',)})


def test_group():
    for i, n, o in (
        ('', 2, ()),
        ('A', 2, (('A',),)),
        ('AB', 2, (('A', 'B'),)),
        ('ABCDE', 2, (('A', 'B'), ('C', 'D'), ('E',))),
    ):
        yield check_group, i, n, o


def check_group(i, n, o):
    eq_(tuple(group(i, n)), tuple(o))


def test_listxxx():
    data = dict(a='a', b='x', c='123')
    keys = listkeys(data)
    values = listvalues(data)
    items = listitems(data)
    types = map(type, (keys, values, items))
    eq_(set(types), set([list]))

    eq_(sorted(keys), ['a', 'b', 'c'])
    eq_(sorted(values), ['123', 'a', 'x'])
    eq_(sorted(items), [('a', 'a'), ('b', 'x'), ('c', '123')])


def test_inverse_mapping_works():
    eq_(inverse_mapping({'a': 123, 'x': 'x'}), {123: 'a', 'x': 'x'})


@raises(ValueError)
def test_inverse_mapping_raises_exception_when_values_arent_unique():
    inverse_mapping({'a': 1, 'b': 1})


def test_is_sorted():
    for sequence, kwargs, result in (
        ((1, 2, 3), {}, True),
        ([1, 2, 3], {}, True),
        ([2, 1], {}, False),
        ([1, 1], {}, True),
        ((), {}, True),
        ([], {}, True),
        ((3, 2, 1), {'reverse': True}, True),
        ((3, 2, 1), {'key': lambda e: -e}, True),
        ((1, 2, 3), {'reverse': True, 'key': lambda e: -e}, True),
    ):
        yield check_is_sorted, sequence, kwargs, result


def check_is_sorted(sequence, kwargs, result):
    eq_(is_sorted(sequence, **kwargs), result)


@raises(TypeError)
def test_is_sorted_fails_on_sets():
    is_sorted(set())


@raises(TypeError)
def test_is_sorted_fails_on_dictionaries():
    is_sorted({})


def test_has_unique_elements():
    eq_(has_unique_elements([1, 2, 3]), True)
    eq_(has_unique_elements([1, 2, 1]), False)


def test_copy_keys_if_present():
    destination = {'a': 'old val a'}
    copy_keys_if_present(
        {'a': 'new val a', 'b': 'val b'},
        destination,
        ['a', 'b', 'c']
    )
    eq_(destination, {'a': 'new val a', 'b': 'val b'})


def test_listmap_works_and_returns_a_list():
    result = listmap(str, [1, 2])
    eq_((result, type(result)), (['1', '2'], list))
