A, B = list(map(int, input().split()))
import math


def prime_numbers(n):
    """n以下の素数列挙"""
    eratosthenes = [True] * (n + 1)
    eratosthenes[1] = False
    prime_list = []
    for i in range(2, n + 1):

        if eratosthenes[i]:
            k = 2
            while True:
                if i * k < n + 1:
                    eratosthenes[i * k] = False
                    k += 1
                else:
                    break
            prime_list.append(i)
    return prime_list


def prime_factorization(n: int):
    factors = []
    tmp_n = n
    for i in range(2, math.ceil(math.sqrt(n)) + 1):
        count_divide = 0
        while True:
            tmp_n = n
            s, r = divmod(tmp_n, i)
            if r == 0:
                count_divide += 1
                n = s
            else:
                break
        if count_divide >= 1:
            factors.append([i, count_divide])
    if tmp_n > 1:
        factors.append([tmp_n, 1])
    return factors


a_b_max = max(A, B)
a_b_min = min(A, B)
max_factors = prime_factorization(a_b_max)
min_factors = prime_factorization(a_b_min)
j = 0
ans = 1
for p, i in max_factors:
    while True:
        if j == len(min_factors):
            break
        if min_factors[j][0] == p:
            ans += 1
            j += 1
        elif min_factors[j][0] < p:
            j += 1
        else:
            break

print(ans)
# ans = 1
# for p in prime_list:
#     a_s, a_r = divmod(A, p)
#     b_s, b_r = divmod(B, p)
#     if A % p == 0 and B % p == 0:
#         ans += 1
