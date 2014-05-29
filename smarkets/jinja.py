from __future__ import absolute_import, division, print_function, unicode_literals

from jinja2 import BytecodeCache


class InMemoryBytecodeCache(BytecodeCache):
    def __init__(self):
        self._storage = {}

    def clear(self):
        self._storage.clear()

    def load_bytecode(self, bucket):
        try:
            cached = self._storage[bucket.key]
        except KeyError:
            pass
        else:
            bucket.bytecode_from_string(cached)

    def dump_bytecode(self, bucket):
        self._storage[bucket.key] = bucket.bytecode_to_string()
