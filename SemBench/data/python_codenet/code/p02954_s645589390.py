import math
from math import gcd,pi,sqrt
INF = float("inf")

import sys
sys.setrecursionlimit(10**6)
import itertools
from collections import Counter,deque
def i_input(): return int(input())
def i_map(): return map(int, input().split())
def i_list(): return list(i_map())
def i_row(N): return [i_input() for _ in range(N)]
def i_row_list(N): return [i_list() for _ in range(N)]
def s_input(): return input()
def s_map(): return input().split()
def s_list(): return list(s_map())
def s_row(N): return [s_input for _ in range(N)]
def s_row_str(N): return [s_list() for _ in range(N)]
def s_row_list(N): return [list(s_input()) for _ in range(N)]


def main():
    s = s_input()

    l = [0 for i in range(len(s))]
    cnt = 0
    flg = "R"

    for n,i in enumerate(s):
        if i == flg:
            cnt += 1
        else:
            if i == "L":
                f = math.ceil(cnt/2)
                b = cnt - f
                l[n-1] = l[n-1] + f
                l[n] = l[n] + b
                flg = "L"
            else:
                b = math.ceil(cnt/2)
                f = cnt - b
                l[n-cnt-1] = l[n-cnt-1] + f
                l[n-cnt] = l[n-cnt] + b
                flg = "R"
            cnt = 1
    b = math.ceil(cnt/2)
    f = cnt - b
    l[n-cnt] = l[n-cnt] + f
    l[n-cnt+1] = l[n-cnt+1] + b

    print(" ".join(map(str,l)))





if __name__=="__main__":
    main()
