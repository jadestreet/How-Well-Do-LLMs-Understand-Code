# import bisect
from collections import Counter, deque # https://note.nkmk.me/python-scipy-connected-components/
# from copy import copy, deepcopy
# from functools import reduce
# from heapq import heapify, heappop, heappush
# from itertools import accumulate, permutations, combinations, combinations_with_replacement, groupby, product
# import math
# import numpy as np  # Pythonのみ！
# from operator import xor
# import re
# from scipy.sparse.csgraph import connected_components  # Pythonのみ！
# ↑cf.  https://note.nkmk.me/python-scipy-connected-components/
# from scipy.sparse import csr_matrix
# import string
import sys
sys.setrecursionlimit(10 ** 5 + 10)
def input(): return sys.stdin.readline().strip()

def resolve():
    L=[]
    for _ in range(3):
        a,b=map(int,input().split())
        L.append(a-1)
        L.append(b-1)
    LL=Counter(L).most_common()
    if LL[0][1]!=2:
        print('NO')
    else:
        print('YES')
    
    



resolve()