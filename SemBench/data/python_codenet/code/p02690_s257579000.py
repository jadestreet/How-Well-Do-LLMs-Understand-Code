import sys
import numpy as np
from math import ceil as C, floor as F, sqrt
from collections import defaultdict as D, Counter as CNT
from functools import reduce as R
 
ALP = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alp = 'abcdefghijklmnopqrstuvwxyz'
def _X(): return sys.stdin.readline().rstrip().split(' ')
def _S(ss): return tuple(ss) if len(ss) > 1 else ss[0]
def S(): return _S(_X())
def Ss(): return list(S())
def _I(ss): return tuple([int(s) for s in ss]) if isinstance(ss, tuple) else int(ss)
def I(): return _I(S())
def _Is(ss): return list(ss) if isinstance(ss, tuple) else [ss]
def Is(): return _Is(I())

x = I()

A = []
As = []
B = []
Bs = []

for i in range(250):
  n = i ** 5
  A.append(i)
  As.append(n)
  B.append(i)
  Bs.append(n)
  B.append(-i)
  Bs.append(-n)

xs = [a-x for a in As]
for i, x in enumerate(xs):
  if x in Bs:
    print(A[i], B[Bs.index(x)])
    break
