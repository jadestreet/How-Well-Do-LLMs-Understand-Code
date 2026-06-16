import sys
sys.setrecursionlimit(10**7)
def LI(): return [int(x) for x in sys.stdin.readline().split()]
def LI_(): return [int(x) - 1 for x in sys.stdin.readline().split()]
def LF(): return [float(x) for x in sys.stdin.readline().split()]
def LS(): return sys.stdin.readline().split()
def II(): return int(sys.stdin.readline())
def SI(): return sys.stdin.readline().strip()
MOD = 10 ** 9 + 7
INF = 10 ** 18

from collections.abc import Sequence, Set
from bisect import bisect_left
from itertools import chain

from heapq import heappush, heappop

class HeapSet():
    # 最小値を O(log n) で取り出せる set. 中身としては、入っているものを set で管理し、順番を heapq で管理しているだけ。
    def __init__(self):
        self._set = set()
        self._list = list()

    def add(self, a):
        if a in self._set:
            return
        else:
            self._set.add(a)
            heappush(self._list, a)

    def remove(self, a):
        if a not in self._set:
            raise ValueError
        else:
            self._set.remove(a)

    def pop(self):
        if not self._set:
            self._list = list()
            raise IndexError
        while True:
            a = self._list[0]
            if a not in self._set:
                heappop(self._list)
                continue
            else:
                break
        self._set.remove(a)
        return a

    def peek(self):
        if not self._set:
            self._list = list()
            raise IndexError
        while True:
            a = self._list[0]
            if a not in self._set:
                heappop(self._list)
                continue
            else:
                break
        return a

    def get_set(self): return self._set
    def get_heapq(self): return self._list
    def get_list(self): return self._list
    def __bool__(self): return True if self._set else False
    def __contains__(self, a): return a in self._set
    def __len__(self): return len(self._set)
    def __repr__(self):
        return "HeapSet(" + (repr(self._set) if self._set else '') + ")"





def main(): 
    N, Q = LI()
    events = []
    for _ in range(N):
        stx = LI()
        # events.append((s - x, x, True))  # S-X, X, add_flag
        # events.append((t - x, x, False))  # T-X, X, add_flag
        events.append((stx[0] - stx[2], stx[2], True))  # S-X, X, add_flag
        events.append((stx[1] - stx[2], stx[2], False))  # T-X, X, add_flag
    for _ in range(Q):
        events.append((II(), INF, -1))
 
    # events.sort(key=lambda x:x[0])  # O(N log N), stable
    events.sort()  # O(N log N), stable, False (==0) < True (==1)
 
    from array import array
    ans = array('i')
    # m = SortedList()
    m = HeapSet()
    # for time, x, add_flag in events:
    change_flag = True
    min_ = INF
    for txa in events:
        if txa[2] == -1:
            if not m:
                ans.append(-1)
                # ans += '-1\n'
            else:
                if change_flag:
                    min_ = m.peek()
                    change_flag = False
                ans.append(min_)
                # ans += str(m[0])+'\n'
        elif txa[2]:
            m.add(txa[1])
            if txa[1] < min_:
                min_ = txa[1]
                change_flag = False
        else:
            m.remove(txa[1])
            if txa[1] == min_ and m:
                min_ = m.peek()
                change_flag = False
            elif not m:
                min_ = INF
                change_flag = False
 
    # for i in ans: print(i)
    # print('\n'.join(map(str, ans)))
    print('\n'.join(map(str, ans.tolist())))

main()