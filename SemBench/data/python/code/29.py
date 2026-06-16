# 29.py — Huffman coding: build tree, encode, decode
import heapq
from typing import Dict, Optional, List, Tuple

class Node:
    __slots__ = ("ch", "freq", "left", "right")
    def __init__(self, ch: Optional[str], freq: int, left: 'Optional[Node]' = None, right: 'Optional[Node]' = None):
        self.ch = ch; self.freq = freq; self.left = left; self.right = right
    def __lt__(self, other: 'Node'):
        return self.freq < other.freq

def freq_table(s: str) -> Dict[str, int]:
    tbl: Dict[str, int] = {}
    for ch in s:
        tbl[ch] = tbl.get(ch, 0) + 1
    return tbl

def build_tree(tbl: Dict[str, int]) -> Optional[Node]:
    heap: List[Tuple[int, int, Node]] = []
    uid = 0
    for ch, f in tbl.items():
        heap.append((f, uid, Node(ch, f)))
        uid += 1
    if not heap:
        return None
    heapq.heapify(heap)
    while len(heap) > 1:
        f1, _, n1 = heapq.heappop(heap)
        f2, _, n2 = heapq.heappop(heap)
        parent = Node(None, f1 + f2, n1, n2)
        heapq.heappush(heap, (parent.freq, uid, parent)); uid += 1
    return heapq.heappop(heap)[2]

def build_code_map(root: Optional[Node]) -> Dict[str, str]:
    codes: Dict[str, str] = {}
    if root is None:
        return codes
    def dfs(n: Node, path: str):
        if n.ch is not None:
            codes[n.ch] = path or "0"
            return
        dfs(n.left, path + "0")
        dfs(n.right, path + "1")
    dfs(root, "")
    return codes

def encode(s: str, codes: Dict[str, str]) -> str:
    out = []
    for ch in s:
        out.append(codes[ch])
    return "".join(out)

def decode(bits: str, root: Optional[Node]) -> str:
    if root is None:
        return ""
    out = []
    node = root
    for b in bits:
        node = node.left if b == "0" else node.right
        if node.ch is not None:
            out.append(node.ch)
            node = root
    return "".join(out)
