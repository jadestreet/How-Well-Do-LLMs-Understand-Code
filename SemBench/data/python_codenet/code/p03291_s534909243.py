#
# 　　  ⋀_⋀　 
#　　  (･ω･)  
# .／ Ｕ ∽ Ｕ＼
#  │＊　合　＊│
#  │＊　格　＊│ 
#  │＊　祈　＊│ 
#  │＊　願　＊│ 
#  │＊　　　＊│ 
#      ￣
#
import sys
sys.setrecursionlimit(10**6)
input=sys.stdin.readline
from math import floor,ceil,sqrt,factorial,hypot,log #log2ないｙｐ
from heapq import heappop, heappush, heappushpop
from collections import Counter,defaultdict,deque
from itertools import accumulate,permutations,combinations,product,combinations_with_replacement
from bisect import bisect_left,bisect_right
from copy import deepcopy
inf=float('inf')
mod = 10**9+7
def pprint(*A): 
    for a in A:     print(*a,sep='\n')
def INT_(n): return int(n)-1
def MI(): return map(int,input().split())
def MF(): return map(float, input().split())
def MI_(): return map(INT_,input().split())
def LI(): return list(MI())
def LI_(): return [int(x) - 1 for x in input().split()]
def LF(): return list(MF())
def LIN(n:int): return [I() for _ in range(n)]
def LLIN(n: int): return [LI() for _ in range(n)]
def LLIN_(n: int): return [LI_() for _ in range(n)]
def LLI(): return [list(map(int, l.split() )) for l in input()]
def I(): return int(input())
def F(): return float(input())
def ST(): return input().replace('\n', '')
#mint
class ModInt:
    def __init__(self, x):
        self.x = x % mod
    
    def __str__(self):
        return str(self.x)
    
    __repr__ = __str__

    def __add__(self, other):
        if isinstance(other, ModInt):
            return ModInt(self.x + other.x)
        else:
            return ModInt(self.x + other)

    __radd__ = __add__
        
    def __sub__(self, other):
        if isinstance(other, ModInt):
            return ModInt(self.x - other.x)
        else:
            return ModInt(self.x - other)

    def __rsub__(self, other):
        if isinstance(other, ModInt):
            return ModInt(other.x - self.x)
        else:
            return ModInt(other - self.x)

    def __mul__(self, other):
        if isinstance(other, ModInt):
            return ModInt(self.x * other.x)
        else:
            return ModInt(self.x * other)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, ModInt):
            return ModInt(self.x * pow(other.x, mod-2,mod))
        else:
            return ModInt(self.x * pow(other, mod - 2, mod))
            
    def __rtruediv(self, other):
        if isinstance(other, self):
            return ModInt(other * pow(self.x, mod - 2, mod))
        else:
            return ModInt(other.x * pow(self.x, mod - 2, mod))
            

    def __pow__(self, other):
        if isinstance(other, ModInt):
            return ModInt(pow(self.x, other.x, mod))
        else:
            return ModInt(pow(self.x, other, mod))
            

    def __rpow__(self, other):
        if isinstance(other, ModInt):
            return ModInt(pow(other.x, self.x, mod))
        else:
            return ModInt(pow(other, self.x, mod))

def main():
    S=ST()
    N=len(S)
    dp = [[ModInt(0)]*4 for _ in range(N)] #dp[i][j]:=i番目までで、ABCのj文字目まで完成している場合の数
    dp[0][0]+=1
    for i,s in enumerate(S):
        if i==0:
            if s in "A?":
                dp[0][1]+=1
                if s == "?":
                    dp[0][0]*=3
            continue

        for j in range(4):
            if s=="?":
                dp[i][j]=3*dp[i-1][j]
            else:
                dp[i][j]=dp[i-1][j]
        
        if s=="A":
            dp[i][1]+=dp[i-1][0]
        elif s=="B":
            dp[i][2]+=dp[i-1][1]
        elif s=="C":
            dp[i][3]+=dp[i-1][2]
        else:
            dp[i][1]+=dp[i-1][0]
            dp[i][2]+=dp[i-1][1]
            dp[i][3]+=dp[i-1][2]

    print(dp[-1][-1])
if __name__ == '__main__':
    main()