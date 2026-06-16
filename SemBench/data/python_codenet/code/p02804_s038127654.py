def prepare(n, MOD):
    # 1! - n! の計算
    f = 1
    factorials = [1]  # 0!の分
    for m in range(1, n + 1):
        f *= m
        f %= MOD
        factorials.append(f)
    # n!^-1 の計算
    inv = pow(f, MOD - 2, MOD)
    # n!^-1 - 1!^-1 の計算
    invs = [1] * (n + 1)
    invs[n] = inv
    for m in range(n, 1, -1):
        inv *= m
        inv %= MOD
        invs[m - 1] = inv

    return factorials, invs

def main():
    n,k=map(int, input().split())
    A=[int(i) for i in input().split()]
    MOD = 10**9 + 7
    fac, invs = prepare(n,MOD)
    ans = 0
    A.sort()

    for i in range(n):
        tmp=0
        tmp2=0
        if i<n-k+1:
            tmp = (fac[n-(i+1)]%MOD * invs[k-1]%MOD * invs[n-(i+1) - (k-1)]%MOD)%MOD
        if i>=k-1:
            tmp2 = (fac[i]%MOD * invs[k-1]%MOD * invs[i-(k-1)]%MOD)%MOD
        #print("最大になる回数", tmp2, " 最小になる回数", tmp, "A[i]", A[i])
        ans = ans%MOD + (tmp2*A[i]%MOD - tmp*A[i]%MOD)%MOD
        ans%=MOD

    if k==1:
        ans = 0
    print(ans)

if __name__ == '__main__':
    main()
