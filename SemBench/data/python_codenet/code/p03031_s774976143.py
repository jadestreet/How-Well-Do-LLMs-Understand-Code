#! /usr/bin/env python3
import sys
sys.setrecursionlimit(10**9)

def mi(): return map(int,input().split())
def ii(): return int(input())
def isp(): return input().split()
def deb(text): print("-------\n{}\n-------".format(text))

INF=10**20
def bit_search(n):
    res = []
    for i in range(2**n):
        st = set()
        for j in range(n): 
            if ((i >> j) & 1):
                st.add(j)
        res.append(st)
    return res

def main():
    N,M=mi()
    X = {}
    for i in range(M):
        inp = list(mi())
        X[i] = inp[1:]
    
    P = list(mi())

    ans = 0
    for combs in bit_search(N):
        res = 0
        for i in range(M):
            on_count = 0
            for j in range(len(X[i])):
                s = X[i][j] - 1 # 0-index
                if s in combs:
                    on_count += 1
            
            if on_count % 2 == P[i]:
                res += 1

        if res == M:
            ans += 1


    print(ans)
                    





if __name__ == "__main__":
    main()