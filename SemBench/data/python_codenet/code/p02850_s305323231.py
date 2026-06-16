# -*- coding: utf-8 -*-
import sys
import math
from bisect import bisect_left
from bisect import bisect_right
import collections
import copy
import heapq
from collections import defaultdict
from heapq import heappop, heappush
import itertools
input = sys.stdin.readline
from collections import defaultdict
from heapq import heappop, heappush

from decimal import *

##### リストの 二分木検索 #####
# bisect_left(lists, 3)
# bisect_right(lists, 3)

##### プライオリティキュー #####
# heapq.heapify(a) #リストaのheap化
# heapq.heappush(a,x) #heap化されたリストaに要素xを追加
# heapq.heappop(a) #heap化されたリストaから最小値を削除＆その最小値を出力

# heapq.heappush(a, -x) #最大値を取り出す時は、pushする時にマイナスにして入れよう
# heapq.heappop(a) * (-1) #取り出す時は、-1を掛けて取り出すこと

##### タプルリストのソート #####
# sorted(ans) #(a, b) -> 1st : aの昇順, 2nd : bの昇順
# sorted(SP, key=lambda x:(x[0],-x[1])) #(a, b) -> 1st : aの昇順, 2nd : bの降順
# sorted(SP, key=lambda x:(-x[0],x[1])) #(a, b) -> 1st : aの降順, 2nd : bの昇順
# sorted(SP, key=lambda x:(-x[0],-x[1])) #(a, b) -> 1st : aの降順, 2nd : bの降順

# sorted(SP, key=lambda x:(x[1])) #(a, b) -> 1st : bの昇順
# sorted(SP, key=lambda x:(-x[1])) #(a, b) -> 1st : bの降順

##### 累乗 #####
# pow(x, y, z) -> x**y % z

##### 割り算の切り上げ #####
# tmp = -(-4 // 3)

##### dict の for文 #####
# for k, v in d.items():
#     print(k, v)

def inputInt(): return int(input())
def inputMap(): return map(int, input().split())
def inputList(): return list(map(int, input().split()))
def inputStr(): return input()[:-1]

inf = float('inf')
mod = 1000000007

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

def main():
	N = inputInt()
	ki = [[] for i in range(N)]
	inp = {}
	ans = [inf for i in range(N-1)]
	ansInt = 0

	for i in range(N-1):
		a,b = inputMap()
		a -= 1
		b -= 1
		ki[a].append(b)
		ki[b].append(a)
		inp[(a,b)] = i

	for i in ki:
		if len(i) > ansInt:
			ansInt = len(i)

	for i in range(N):
		ko = ki[i]
		dame = []
		mi = []
		for j in ko:
			#print("{} {} {}".format(i,j,ko))
			if i < j:
				mi.append(j)
			else:
				dame.append(ans[inp[(j,i)]])
		#dame.sort()
		mark = 0
		for j in mi:
			for ii in range(mark,ansInt+1):
				if ii in dame:
					pass
				else:
					ans[inp[(i,j)]] = ii
					dame.append(ii)
					break
				mark += 1
		#print(ans)

	#print(ki)
	#print(inp)
	#print(ans)

	print(ansInt)
	for i in ans:
		print(i+1)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
# N 個のボールを K グループに分ける場合のパターン数
def sunuke(N, K, mod=10**9+7):
	if N < K or K-1 < 0:
		return 0
	else:
		return combination(N-1, K-1, mod)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
# nCr mod m
# rがn/2に近いと非常に重くなる
def combination(n, r, mod=10**9+7):
    r = min(r, n-r)
    res = 1
    for i in range(r):
        res = res * (n - i) * modinv(i+1, mod) % mod
    return res

# mを法とするaの乗法的逆元
def modinv(a, mod=10**9+7):
    return pow(a, mod-2, mod)

def egcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = egcd(b % a, a)
        return g, x - (b // a) * y, y

# nHr mod m
# 問題によって、combination()を切り替えること
def H(n, r, mod=10**9+7):
	# comb = Combination(n+r-1, mod)
	# return comb(n+r-1, r)
    return combination(n+r-1, r, mod)


class Combination:
    """
    O(n)の前計算を1回行うことで，O(1)でnCr mod mを求められる
    n_max = 10**6のとき前処理は約950ms (PyPyなら約340ms, 10**7で約1800ms)
    使用例：
    comb = Combination(1000000)
    print(comb(5, 3))  # 10
    """
    def __init__(self, n_max, mod=10**9+7):
        self.mod = mod
        self.modinv = self.make_modinv_list(n_max)
        self.fac, self.facinv = self.make_factorial_list(n_max)

    def __call__(self, n, r):
        return self.fac[n] * self.facinv[r] % self.mod * self.facinv[n-r] % self.mod

    def make_factorial_list(self, n):
        # 階乗のリストと階乗のmod逆元のリストを返す O(n)
        # self.make_modinv_list()が先に実行されている必要がある
        fac = [1]
        facinv = [1]
        for i in range(1, n+1):
            fac.append(fac[i-1] * i % self.mod)
            facinv.append(facinv[i-1] * self.modinv[i] % self.mod)
        return fac, facinv

    def make_modinv_list(self, n):
        # 0からnまでのmod逆元のリストを返す O(n)
        modinv = [0] * (n+1)
        modinv[1] = 1
        for i in range(2, n+1):
            modinv[i] = self.mod - self.mod//i * modinv[self.mod%i] % self.mod
        return modinv

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
# dfs のサンプル
def dfs(graph,parent,counter,edge):
    stk = []
    stk.append(edge)
    while len(stk) > 0:
        p = stk.pop()
        for e in graph[p]:
            if parent[p] == e:
                continue
            else:
                parent[e] = p
                counter[e] += counter[p]
                stk.append(e)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
if __name__ == "__main__":
	main()
