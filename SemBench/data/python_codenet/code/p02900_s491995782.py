# -*- coding: utf-8 -*-
# D

import sys
from collections import defaultdict, deque
from heapq import heappush, heappop
import math
import bisect
input = sys.stdin.readline

# 再起回数上限変更
# sys.setrecursionlimit(1000000)

a, b = map(int, input().split())

class Mint(object):
    """ 整数のお役立ち計算
    - 繰り返し二乗法で効率的にn**kを求める（必要であればmodを指定）
    - 素数判定
    - 素因数分解
    - 約数列挙
    - nCrの計算(ピンポイントで求める or あるnまでのnCrを計算するのに必要な情報を一気に求める）
    - ToDo:
    # divisor : 配列をsortしているため遅い可能性あり
    """

    def gcd(self, a, b):
        # ユークリッドの互除法を用いる
        while b:
            a, b = b, a % b
        return a

    def lcm(self, a, b):
        return a * b // self.gcd(a, b)

    @staticmethod
    def cmb_(n, r):
        """ 普通にnCrを求める
        >>> p = Mint()
        >>> p.cmb_(10, 2)
        45
        """
        from operator import mul
        from functools import reduce

        r = min(n - r, r)
        if r == 0:
            return 1
        over = reduce(mul, range(n, n - r, -1))
        under = reduce(mul, range(1, r + 1))
        return over // under

    def cmb(self, n, r, mod: int = 10 ** 9 + 7):
        """ 事前にあるnまでの範囲で、nCrを高速に計算する
        >>> p = Mint()
        >>> p.cmb_prep(10)
        >>> p.cmb(10, 2)
        45
        """
        if (r < 0) or (r > n):
            return 0
        r = min(r, n - r)
        return self.g1[n] * self.g2[r] * self.g2[n - r] % mod

    def cmb_prep(self, N: int, mod: int = 10 ** 9 + 7):
        self.g1 = [1, 1]  # 元テーブル
        self.g2 = [1, 1]  # 逆元テーブル
        inverse = [0, 1]  # 逆元テーブル計算用テーブル

        for i in range(2, N + 1):
            self.g1.append((self.g1[-1] * i) % mod)
            inverse.append((-inverse[mod % i] * (mod // i)) % mod)
            self.g2.append((self.g2[-1] * inverse[-1]) % mod)

    @staticmethod
    def iterated_power(z: int, n: int, mod=None) -> int:
        """ 繰り返し二乗法でn**kを求める（再帰処理は使わない）
        >>> p = Mint()
        >>> p.iterated_power(3, 10)
        59049
        >>> p.iterated_power(3, 10, 10)
        9
        """
        beta = bin(n)[2:]

        Z, q, t = z, 0, len(beta)
        while beta[t - q - 1] == '0':
            Z = Z * Z
            if mod is not None:
                Z = Z % mod
            q += 1
        result = Z

        for k in range(q + 1, t):
            Z = Z * Z
            if mod is not None:
                Z = Z % mod
            if beta[t - k - 1] == '1':
                result = result * Z
                if mod is not None:
                    result = result % mod

        if mod is not None:
            result = result % mod

        return result

    @staticmethod
    def factorization(n: int) -> dict:
        from collections import defaultdict

        arr = defaultdict(int)
        temp = n
        for i in range(2, int(-(-n ** 0.5 // 1)) + 1):
            if temp % i == 0:
                cnt = 0
                while temp % i == 0:
                    cnt += 1
                    temp //= i
                arr[i] = cnt

        if temp != 1:
            arr[temp] = 1

        if arr == []:
            arr[n] = 1

        return arr

    @staticmethod
    def enumerate_prime(n: int) -> (list, dict, list):
        """
        n以下の素数を列挙する
        何で割るかを記録しておくことで、素因数分解が高速にできる
        >>> p = Mint()
        >>> p.enumerate_prime(11)
        ([2, 3, 5, 7, 11], {2: 0, 3: 1, 5: 2, 7: 3, 11: 4}, [0, 1, 2, 3, 2, 5, 3, 7, 2, 3, 5, 11])
        """

        lis_prime = [True] * (n+1)
        lis_prime[0] = False
        lis_prime[1] = False

        primes = []
        div_prime = [i for i in range(n + 1)]
        primes_idx = {}

        cnt = 0
        for i in range(2, n+1):
            if lis_prime[i]:
                primes.append(i)
                primes_idx[i] = cnt
                cnt += 1

                j = 2 * i
                while True:
                    if j > n:
                        break
                    lis_prime[j] = False
                    div_prime[j] = i
                    j += i

        return primes, primes_idx, div_prime

    @staticmethod
    def is_prime(n: int) -> bool:
        """
        素数判定
        >>> p = Mint()
        >>> p.is_prime(2)
        True
        >>> p.is_prime(43)
        True
        >>> p.is_prime(4)
        False
        """

        if n == 1:
            return False
        if n == 2:
            return True

        for i in range(2, n):
            if n % i == 0:
                return False
            if i * i > n:
                return True

    @staticmethod
    def divisor(n: int) -> list:
        """
        約数列挙
        >>> p = Mint()
        >>> p.divisor(6)
        [1, 2, 3, 6]
        """
        res = []
        if n == 1:
            return [1]

        for i in range(1, n):
            if n % i == 0:
                res.append(i)
                if i != n / i:
                    res.append(int(n / i))
            if (i+1) * (i+1) > n:
                res.sort()
                return res

mint = Mint()
c = mint.gcd(a, b)
# print(c)
candidates = mint.divisor(c)[1:]
# print(candidates)
res = [True] * len(candidates)

for idx, i in enumerate(candidates):
    # if i > len(candidates)**.5:
    #     break
    for j in range(idx+1, len(candidates)):
        if candidates[j] % i == 0:
            res[j] = False

ans = 1
for i in res:
    if i:
        ans += 1

print(ans)