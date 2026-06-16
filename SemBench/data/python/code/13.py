# 13.py — Reverse a singly linked list (iterative)
from typing import Optional

class ListNode:
    def __init__(self, val: int, next: 'Optional[ListNode]' = None) -> None:
        self.val = val
        self.next = next

def _reverse_iter(head: Optional[ListNode]) -> Optional[ListNode]:
    prev, curr = None, head
    while curr is not None:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev

def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    return _reverse_iter(head)
