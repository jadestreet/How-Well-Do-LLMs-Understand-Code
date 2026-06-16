# 28.py — Interval tree supporting add, remove, and overlap queries
from typing import Optional, List, Tuple

class Node:
    __slots__ = ("lo", "hi", "max_hi", "left", "right")
    def __init__(self, lo: int, hi: int) -> None:
        self.lo = lo; self.hi = hi
        self.max_hi = hi
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

class IntervalTree:
    def __init__(self) -> None:
        self.root: Optional[Node] = None

    def _update(self, n: Optional[Node]) -> None:
        if not n: return
        n.max_hi = n.hi
        if n.left and n.left.max_hi > n.max_hi: n.max_hi = n.left.max_hi
        if n.right and n.right.max_hi > n.max_hi: n.max_hi = n.right.max_hi

    def _insert(self, n: Optional[Node], lo: int, hi: int) -> Node:
        if n is None:
            return Node(lo, hi)
        if lo < n.lo:
            n.left = self._insert(n.left, lo, hi)
        else:
            n.right = self._insert(n.right, lo, hi)
        self._update(n)
        return n

    def add(self, lo: int, hi: int) -> None:
        if lo > hi: lo, hi = hi, lo
        self.root = self._insert(self.root, lo, hi)

    def _overlap(self, a: Tuple[int,int], b: Tuple[int,int]) -> bool:
        return a[0] <= b[1] and b[0] <= a[1]

    def query(self, lo: int, hi: int) -> List[Tuple[int,int]]:
        res: List[Tuple[int,int]] = []
        def dfs(n: Optional[Node]) -> None:
            if not n: return
            if self._overlap((lo,hi), (n.lo, n.hi)): res.append((n.lo, n.hi))
            if n.left and n.left.max_hi >= lo: dfs(n.left)
            if n.right and n.lo <= hi: dfs(n.right)
        dfs(self.root)
        return res

    def _min_node(self, n: Node) -> Node:
        while n.left:
            n = n.left
        return n

    def _remove(self, n: Optional[Node], lo: int, hi: int) -> Optional[Node]:
        if not n: return None
        if lo < n.lo:
            n.left = self._remove(n.left, lo, hi)
        elif lo > n.lo:
            n.right = self._remove(n.right, lo, hi)
        else:
            if n.hi == hi:
                if not n.left: return n.right
                if not n.right: return n.left
                succ = self._min_node(n.right)
                n.lo, n.hi = succ.lo, succ.hi
                n.right = self._remove(n.right, succ.lo, succ.hi)
            else:
                n.right = self._remove(n.right, lo, hi)
        self._update(n)
        return n

    def remove(self, lo: int, hi: int) -> None:
        if lo > hi: lo, hi = hi, lo
        self.root = self._remove(self.root, lo, hi)
