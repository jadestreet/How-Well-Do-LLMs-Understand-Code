# 24.py — Simple event scheduler using a min-heap
import heapq
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

@dataclass(order=True)
class Event:
    time: int
    priority: int
    action: Callable[[], None] = field(compare=False)
    cancelled: bool = field(default=False, compare=False)

class Scheduler:
    def __init__(self) -> None:
        self._q: List[Event] = []
        self._now = 0

    def schedule(self, delay: int, action: Callable[[], None], priority: int = 0) -> Event:
        evt = Event(self._now + delay, priority, action)
        heapq.heappush(self._q, evt)
        return evt

    def cancel(self, evt: Event) -> None:
        evt.cancelled = True

    def run_until(self, end_time: int) -> None:
        while self._q and self._q[0].time <= end_time:
            evt = heapq.heappop(self._q)
            self._now = evt.time
            if evt.cancelled:
                continue
            try:
                evt.action()
            except Exception:
                # swallow errors to keep loop running
                pass
        self._now = end_time

    def now(self) -> int:
        return self._now
