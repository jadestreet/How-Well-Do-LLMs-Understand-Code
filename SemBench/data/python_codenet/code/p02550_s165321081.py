# -*- coding: utf-8 -*-

def input_int_array():
    return map(int, input().split())


def answer(n, x, m):
    a1 = x
    ai = a1
    loop_start = -1
    loop_end = n
    a[1] = a1
    ans = a1
    for i in range(2, n + 1):
        ai = ai*ai % m
        a.append(ai)
        ans += ai
        for j in range(1, i):
            if a[j] == ai:
                loop_start = j
                loop_end = i
                break
        if loop_start >= 0:
            break
    if loop_start < 0 or ai == 0:
        print(ans)
        return
    ans -= ai
    loop_count, remaining = divmod(n - (loop_start - 1), loop_end - loop_start)
    if loop_count > loop_start:
        start_ans = 0
        for i in range(1, loop_start):
            start_ans += a[i]
        loop_sum = ans - start_ans
        ans += loop_sum * (loop_count-1)
        for i in range(loop_start, loop_start + remaining):
            ans += a[i]
    else:
        for i in range(loop_start, loop_end):
            if i < remaining:
                ans += a[i]
            loop_sum += a[i]
        ans += loop_sum * (loop_count-1)
    print(ans)


n, x, m = input_int_array()
a = [0, 0]

answer(n, x, m)
