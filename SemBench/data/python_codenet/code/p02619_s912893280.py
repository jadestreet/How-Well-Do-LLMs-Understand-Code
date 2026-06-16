# -*- coding: utf-8 -*-
from sys import stdin
from operator import itemgetter
from collections import deque, Counter
import math
import pprint
from functools import reduce
import numpy as np
# stdin = open("sample.txt")

MOD = 1000000007
INF = float('inf')
alpha = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]

def keta(kazu): # 入力されたintを桁ごとに分解，リストで出力
    kazu_str = str(kazu)
    kazu_list = [int(kazu_str[i]) for i in range(0, len(kazu_str))]
    return kazu_list

def gcd(*numbers): # 最小公倍数
    return reduce(math.gcd, numbers)

def combination(m,n): # mCn
    
    if n > m:
        return 'すまん'
    return math.factorial(m) // (math.factorial(m-n) * math.factorial(n))

def pow_k(x,n):  # (x**n)の計算の高速化
    if n == 0:
        return 1
    K = 1
    while n > 1:
        if n % 2 != 0:
            K *= x
        x *= x
        n //= 2
    return K * x

def fact(n): # nの素因数分解の結果を辞書で出力 fuct(24) → {2: 3, 3: 1}
    arr = {}
    temp = n
    for i in range(2,int(n**0.5)+1):
        if temp % i == 0:
            cnt = 0
            while temp % i == 0:
                cnt += 1
                temp //= i
            arr[i] = cnt
    if temp != 1:
        arr[temp] = 1
    if arr == {}:
        arr[n] = 1
    return arr

def main():
    d = int(stdin.readline().rstrip())
    c = list(map(int,[int(x) for x in stdin.readline().rstrip().split()]))
    table = []
    last = [0]*26
    score = 0
    for _ in range(d):
        table.append(list(map(int,[int(x) for x in stdin.readline().rstrip().split()])))
    for D in range(d):
        go = int(stdin.readline().rstrip()) - 1
        for i in range(26):
            if i == go:
                score += table[D][i]
                last[i] = D+1
                # print(table[D][i])
            else:
                score -= c[i]*(D+1-last[i])
                # print(c[i]*(D+1-last[i]))
        print(score)
main()