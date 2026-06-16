from collections import deque
from heapq import heapify,heappop,heappush,heappushpop
from copy import copy,deepcopy
from itertools import product,permutations,combinations,combinations_with_replacement
from collections import defaultdict,Counter
from bisect import bisect_left,bisect_right
# from math import gcd,ceil,floor,factorial
# from fractions import gcd
from functools import reduce
from pprint import pprint
# from statistics import mean,median,mode

INF = float("inf")

def mycol(data,col):
    return [ row[col] for row in data ]

def mysort(data,col,reverse_flag):
    data.sort(key=lambda x:x[col],reverse=reverse_flag)
    return data

def mymax(data):
    M = -1*float("inf")
    for i in range(len(data)):
        m = max(data[i])
        M = max(M,m)
    return M

def mymin(data):
    m = float("inf")
    for i in range(len(data)):
        M = min(data[i])
        m = min(m,M)
    return m

def mycount(ls,x):
    # lsはソート済みであること
    l = bisect_left(ls,x)
    r = bisect_right(ls,x)
    return (r-l)

def myoutput(ls,space=True):
    if space:
        if len(ls)==0:
            print(" ")
        elif type(ls[0])==str:
            print(" ".join(ls))
        elif type(ls[0])==int:
            print(" ".join(map(str,ls)))
        else:
            print("Output Error")
    else:
        if len(ls)==0:
            print("")
        elif type(ls[0])==str:
            print("".join(ls))
        elif type(ls[0])==int:
            print("".join(map(str,ls)))
        else:
            print("Output Error")

def I():
    return int(input())

def MI():
    return map(int,input().split())

def RI():
    return list(map(int,input().split()))

def CI(n):
    return [ int(input()) for _ in range(n) ]

def LI(n):
    return [ list(map(int,input().split())) for _ in range(n) ]

def S():
    return input()

def MS():
    return input().split()

def RS():
    return list(input().split())

def CS(n):
    return [ input() for _ in range(n) ]

def LS(n):
    return [ list(input().split()) for _ in range(n) ]

n = I()

# 数字nを10進数からb進数へ変換
def base10to(n,b):
    if (int(n/b)):
        return base10to(int(n/b), b) + str(n%b)
    return str(n%b)

# 数字numをb進数から10進数へ変換
def base10from(num, b):
    n = 0
    numlist = list(num);
    while (numlist):
        n *= b
        n += int(numlist.pop(0))
    return n

count = 0

for i in range(3,10):
    m = 3**i
    for j in range(m):
        s = list(base10to(j,3))
        a = "".join(s)
        b = a.zfill(i)
        c = list(b)
        for k in range(i):
            if c[k]=="0":
                c[k] = "3"
            elif c[k]=="1":
                c[k] = "5"
            elif c[k]=="2":
                c[k] = "7"
            else:
                print("E")
        d = "".join(c)
        e = int(d)
        if e<=n:
            if len(set(c))==3:
                count += 1
            else:
                pass
        else:
            print(count)
            exit()

print(count)
exit()