# 22.py — LFU Cache with O(1) get/put using frequency lists
from collections import defaultdict, OrderedDict
from typing import Dict, Any

class LFUCache:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.size = 0
        self.freq_map: Dict[int, OrderedDict] = defaultdict(OrderedDict)  # freq -> keys in LRU order
        self.key_map: Dict[Any, Any] = {}  # key -> (value, freq)
        self.min_freq = 0

    def _update_freq(self, key: Any) -> None:
        value, freq = self.key_map[key]
        # remove from current freq list
        od = self.freq_map[freq]
        od.pop(key)
        if not od and self.min_freq == freq:
            self.min_freq += 1
        # add to next freq
        freq += 1
        self.key_map[key] = (value, freq)
        self.freq_map[freq][key] = value

    def get(self, key: Any):
        if key not in self.key_map:
            return None
        self._update_freq(key)
        return self.key_map[key][0]

    def put(self, key: Any, value: Any) -> None:
        if self.capacity == 0:
            return
        if key in self.key_map:
            # update value and freq
            _, freq = self.key_map[key]
            self.key_map[key] = (value, freq)
            self._update_freq(key)
            return
        if self.size >= self.capacity:
            # evict least frequently used, then least recently used among them
            od = self.freq_map[self.min_freq]
            evict_key, _ = od.popitem(last=False)
            self.key_map.pop(evict_key)
            self.size -= 1
        # insert
        self.key_map[key] = (value, 1)
        self.freq_map[1][key] = value
        self.min_freq = 1
        self.size += 1
