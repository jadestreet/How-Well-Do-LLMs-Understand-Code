from sys import stdin, setrecursionlimit


def factorization(n):
    arr = {}
    temp = n
    for i in range(2, int(-(-n**0.5//1))+1):
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


def main():
    input = stdin.buffer.readline
    n = int(input())

    mods = {}

    for i in range(1, n + 1):
        tmp = factorization(i)
        for j in tmp:
            if j in mods:
                mods[j] += tmp[j]
            else:
                mods[j] = tmp[j]

    c3 = 0
    c5 = 0
    c15 = 0
    c25 = 0
    c75 = 0

    for k in mods:
        if 3 <= mods[k] + 1 < 5:
            c3 += 1
        if 5 <= mods[k] + 1 < 15:
            c5 += 1
        if 15 <= mods[k] + 1 < 25:
            c15 += 1
        if 25 <= mods[k] + 1 < 75:
            c25 += 1
        if mods[k] + 1 >= 75:
            c75 += 1

    ans = 0
    ans += (c5 + c15 + c25 + c75) * (c5 + c15 + c25 + c75 - 1) // 2 * (c3 + c5 + c15 + c25 + c75 - 2)
    ans += (c15 + c25 + c75) * (c5 + c15 + c25 + c75 - 1)
    ans += (c25 + c75) * (c3 + c5 + c15 + c25 + c75 - 1)
    ans += c75

    print(ans)


if __name__ == "__main__":
    setrecursionlimit(10000)
    main()
