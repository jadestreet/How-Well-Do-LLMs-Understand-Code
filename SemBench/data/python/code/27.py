# 27.py — Trie with insert, search, delete, and autocomplete
from typing import Dict, List

class TrieNode:
    __slots__ = ("children", "end")
    def __init__(self) -> None:
        self.children: Dict[str, TrieNode] = {}
        self.end: bool = False

class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.end = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.end

    def _delete(self, node: TrieNode, word: str, i: int) -> bool:
        if i == len(word):
            if not node.end:
                return False
            node.end = False
            return len(node.children) == 0
        ch = word[i]
        if ch not in node.children:
            return False
        should_prune = self._delete(node.children[ch], word, i + 1)
        if should_prune:
            del node.children[ch]
        return not node.end and len(node.children) == 0

    def delete(self, word: str) -> None:
        self._delete(self.root, word, 0)

    def _collect(self, node: TrieNode, prefix: str, out: List[str]) -> None:
        if node.end:
            out.append(prefix)
        for ch, nxt in node.children.items():
            self._collect(nxt, prefix + ch, out)

    def autocomplete(self, prefix: str) -> List[str]:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        out: List[str] = []
        self._collect(node, prefix, out)
        return out
