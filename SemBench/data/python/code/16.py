# 16.py — Simple LRU cache built on OrderedDict
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.store = OrderedDict()

    def _evict_if_needed(self) -> None:
        while len(self.store) > self.capacity:
            self.store.popitem(last=False)

    def get(self, key):
        if key not in self.store:
            return None
        val = self.store.pop(key)
        self.store[key] = val
        return val

    def put(self, key, value) -> None:
        if key in self.store:
            self.store.pop(key)
        self.store[key] = value
        self._evict_if_needed()
