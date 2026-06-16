from collections import defaultdict
import sys
input = sys.stdin.readline

# エラトステネスの篩
#############################################################
def get_sieve_of_eratosthenes(n):
    if not isinstance(n, int):
        raise TypeError('n is int type.')
    if n < 2:
        raise ValueError('n is more than 2')
    prime = [2]
    limit = int(n**0.5)
    data = [i + 1 for i in range(2, n, 2)]
    while True:
        p = data[0]
        if limit <= p:
            return prime + data
        prime.append(p)
        data = [e for e in data if e % p != 0]
#############################################################

# 素因数分解、リストで返す
#############################################################
def prime_factorize(n, prime_list):
    a = []
    for p in prime_list:
        if p * p > n:
            break
        while True:
            if n % p == 0:
                a.append(p)
                n //= p
            else:
                break
    if n != 1:
        a.append(n)
    a.sort()
    return a
#############################################################


N = int(input())
A = list(map(int, input().split()))

data = set(get_sieve_of_eratosthenes(10**6))

primes = defaultdict(int)

for i in range(N):
    p = prime_factorize(A[i], data)
    p_set = set(p)
    for pi in p_set:
        primes[pi] += 1

# print(primes)

if len(primes) == 0:
    print("pairwise coprime")
    exit()

max_cnt = max(primes.values())
min_cnt = min(primes.values())

if max_cnt == 1:
    print("pairwise coprime")
elif max_cnt != N:
    print("setwise coprime")
else:
    print("not coprime")
