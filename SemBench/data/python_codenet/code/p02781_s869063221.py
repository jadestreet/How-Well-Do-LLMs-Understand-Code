import sys
sys.setrecursionlimit(10**7)
def LI(): return [int(x) for x in sys.stdin.readline().split()]
def LI_(): return [int(x) - 1 for x in sys.stdin.readline().split()]
def LF(): return [float(x) for x in sys.stdin.readline().split()]
def LS(): return sys.stdin.readline().split()
def II(): return int(sys.stdin.readline())
def SI(): return sys.stdin.readline().strip()
def LILI(n): return [LI() for _ in range(n)]
INF = 10 ** 18
MOD = 10 ** 9 + 7

'''MEMO:

'''

def main(): 
    N = II()
    K = II()

    keta_N = len(str(N))

    ans = 0

    # 1桁の数
    if K == 1: ans += min(9, N)
    else: pass
    if N < 10:
        print(ans)
        return

    # 2桁の数
    if K == 1:
        for i in range(10, 100, 10):
            if i <= N:
                ans += 1
    elif K == 2:
        for i in range(10, 100, 1):
            if i%10 == 0:
                continue
            elif i <= N:
                ans += 1
    else: pass
    if N < 100:
        print(ans)
        return

    # 3桁以上, keta_N桁未満
    if K == 1:
        ans += 9 * (keta_N - 3)
    else:
        for keta in range(3, keta_N):
            if K == 2:
                ans += 9 * (keta-1) * 9
            else:
                ans += (9 * (keta-1) * (keta-2) * 9 * 9)//2

    # keta_N桁の数
    # すべて生成しても 10**5 個程度なので、すべて生成して N と比較してみる。
    if K == 1:
        for i in range(1, 10):
            if i * 10**(keta_N - 1) <= N:
                ans += 1

    elif K == 2:
        for i in range(1, 10):
            for j in range(1, 10):
                for k in range(0, keta_N-1):
                    if i * 10**(keta_N - 1) + j * 10**k <= N:
                        ans += 1

    elif K == 3:
        for i in range(1, 10):
            if i < int(str(N)[0]):  # 10**7 のループなので愚直で回るはずだけれど、ちょっと高速化。
                ans += ((keta_N - 1) * (keta_N - 2) * 9 * 9)//2
                continue
            elif i > int(str(N)[0]):
                break
            for j in range(1, 10):
                for k in range(0, keta_N-1):
                    for l in range(1, 10):
                        for m in range(0, keta_N-1):
                            if k <= m: continue
                            if i * 10**(keta_N - 1) + j * 10**k + l * 10**m <= N:
                                ans += 1

    print(ans)

main()