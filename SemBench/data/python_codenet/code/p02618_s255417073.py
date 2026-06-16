import os
import sys

import numpy as np


def solve(inp):
    def bitree_sum(bit, t, i):
        s = 0
        while i > 0:
            s += bit[t, i]
            i ^= i & -i
        return s

    def bitree_add(bit, n, t, i, x):
        while i <= n:
            bit[t, i] += x
            i += i & -i

    def bitree_lower_bound(bit, n, d, t, x):
        sum_ = 0
        pos = 0
        for i in range(d, -1, -1):
            k = pos + (1 << i)
            if k <= n and sum_ + bit[t, k] < x:
                sum_ += bit[t, k]
                pos += 1 << i
        return pos + 1

    def initial_score(d, ccc, sss):
        bit_n = d + 3
        bit = np.zeros((26, bit_n), dtype=np.int64)
        INF = 10 ** 18
        for t in range(26):
            bitree_add(bit, bit_n, t, bit_n - 1, INF)

        ttt = np.zeros(d, dtype=np.int64)
        last = np.full(26, -1, dtype=np.int64)
        score = 0

        for i in range(d):
            best_t = 0
            best_diff = -INF
            costs = ccc * (i - last)
            costs_sum = costs.sum()

            for t in range(26):
                tmp_diff = sss[i, t] - costs_sum + costs[t]
                if best_diff < tmp_diff:
                    best_t = t
                    best_diff = tmp_diff
            ttt[i] = best_t
            last[best_t] = i
            score += best_diff
            bitree_add(bit, bit_n, best_t, i + 2, 1)

        return bit, score, ttt

    def calculate_score(d, ccc, sss, ttt):
        last = np.full(26, -1, dtype=np.int64)
        score = 0

        for i in range(d):
            t = ttt[i]
            last[t] = i
            score += sss[i, t] - (ccc * (i - last)).sum()

        return score

    def pinpoint_change(bit, bit_n, bit_d, d, ccc, sss, ttt, permissible):
        cd = np.random.randint(0, d)
        ct = np.random.randint(0, 26)
        while ttt[cd] == ct:
            ct = np.random.randint(0, 26)

        diff = 0
        t = ttt[cd]
        k = bitree_sum(bit, t, cd + 2)
        c = bitree_lower_bound(bit, bit_n, bit_d, t, k - 1) - 2
        e = bitree_lower_bound(bit, bit_n, bit_d, t, k + 1) - 2
        b = ccc[t]
        diff -= b * (cd - c) * (e - cd)
        diff -= sss[cd, t]

        k = bitree_sum(bit, ct, cd + 2)
        c = bitree_lower_bound(bit, bit_n, bit_d, ct, k) - 2
        e = bitree_lower_bound(bit, bit_n, bit_d, ct, k + 1) - 2
        b = ccc[ct]
        diff += b * (cd - c) * (e - cd)
        diff += sss[cd, ct]

        if diff > permissible:
            bitree_add(bit, bit_n, t, cd + 2, -1)
            bitree_add(bit, bit_n, ct, cd + 2, 1)
            ttt[cd] = ct
        else:
            diff = 0

        return diff

    def swap_change(bit, bit_n, bit_d, d, ccc, sss, ttt, permissible):
        dd = np.random.randint(1, 14)
        cd1 = np.random.randint(0, d - dd)
        cd2 = cd1 + dd
        ct1 = ttt[cd1]
        ct2 = ttt[cd2]
        if ct1 == ct2:
            return 0

        diff = 0
        k = bitree_sum(bit, ct1, cd1 + 2)
        c = bitree_lower_bound(bit, bit_n, bit_d, ct1, k - 1) - 2
        e = bitree_lower_bound(bit, bit_n, bit_d, ct1, k + 1) - 2
        diff += ccc[ct1] * (e + c - cd1 - cd2)
        k = bitree_sum(bit, ct2, cd2 + 2)
        c = bitree_lower_bound(bit, bit_n, bit_d, ct2, k - 1) - 2
        e = bitree_lower_bound(bit, bit_n, bit_d, ct2, k + 1) - 2
        diff -= ccc[ct2] * (e + c - cd1 - cd2)
        diff -= sss[cd1, ct1] + sss[cd2, ct2]
        diff += sss[cd1, ct2] + sss[cd2, ct1]

        if diff > permissible:
            bitree_add(bit, bit_n, ct1, cd1 + 2, -1)
            bitree_add(bit, bit_n, ct1, cd2 + 2, 1)
            bitree_add(bit, bit_n, ct2, cd1 + 2, 1)
            bitree_add(bit, bit_n, ct2, cd2 + 2, -1)
            ttt[cd1] = ct2
            ttt[cd2] = ct1
        else:
            diff = 0

        return diff

    d = inp[0]
    ccc = inp[1:27]
    sss = np.zeros((d, 26), dtype=np.int64)
    for r in range(d):
        sss[r] = inp[27 + r * 26:27 + (r + 1) * 26]

    bit, score, ttt = initial_score(d, ccc, sss)
    bit_n = d + 3
    bit_d = int(np.log2(bit_n))
    loop = 5 * 10 ** 6
    permissible_min = -2000.0
    method_border = 0.8
    best_score = score
    best_ttt = ttt.copy()

    for lp in range(loop):
        permissible = (1 - lp / loop) * permissible_min
        if np.random.random() < method_border:
            diff = pinpoint_change(bit, bit_n, bit_d, d, ccc, sss, ttt, permissible)
        else:
            diff = swap_change(bit, bit_n, bit_d, d, ccc, sss, ttt, permissible)
        score += diff

        # print(lp, score, calculate_score(d, ccc, sss, ttt))

        if score > best_score:
            best_score = score
            best_ttt = ttt.copy()

    return best_ttt + 1


if sys.argv[-1] == 'ONLINE_JUDGE':
    from numba.pycc import CC

    cc = CC('my_module')
    cc.export('solve', '(i8[:],)')(solve)
    cc.compile()
    exit()

if os.name == 'posix':
    # noinspection PyUnresolvedReferences
    from my_module import solve
else:
    from numba import njit

    solve = njit('(i8[:],)', cache=True)(solve)
    print('compiled', file=sys.stderr)

inp = np.fromstring(sys.stdin.read(), dtype=np.int64, sep=' ')
ans = solve(inp)
print('\n'.join(map(str, ans)))
