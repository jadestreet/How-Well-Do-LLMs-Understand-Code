#                               #
    # author : samars_diary #
    # 16-09-2020 │ 18:28:11 #
#                               #

import sys, os.path, math

#if(os.path.exists('input.txt')):
    #sys.stdin = open('input.txt',"r")
    #sys.stdout = open('output.txt',"w")

sys.setrecursionlimit(10 ** 5)

mod =  10**9+7
def i(): return sys.stdin.readline().strip()
def ii(): return int(sys.stdin.readline())
def li(): return list(sys.stdin.readline().strip())
def mii(): return map(int, sys.stdin.readline().split())
def lii(): return list(map(int, sys.stdin.readline().strip().split()))

#print=sys.stdout.write

def solve():
    a=ii();print((pow(10,a,mod)+pow(8,a,mod)-2*pow(9,a,mod))%mod)
for _ in range(1):
    solve()