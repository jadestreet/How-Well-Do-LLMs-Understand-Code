class Factorial():
    def __init__(self, n, mod):
        self.mod = mod
        self.fct = [0 for _ in range(n + 1)]
        self.inv = [0 for _ in range(n + 1)]
        self.fct[0] = 1
        self.inv[0] = 1
        for i in range(n):
            self.fct[i + 1] = self.fct[i] * (i + 1) % mod
        self.inv[n] = pow(self.fct[n], mod - 2, mod)
        for i in range(n)[::-1]:
            self.inv[i] = self.inv[i + 1] * (i + 1) % mod
            
    def comb(self, m, k):
        if m < k: return 0
        return self.fct[m] * self.inv[k] * self.inv[m - k] % self.mod

MOD = 1000000007
K = int(input())
S = len(input())
F = Factorial(K + S + 1, MOD)
res = 0
for i in range(S, K + S + 1):
    res += F.comb(K + S, i) * pow(25, K + S - i, MOD)
    res %= MOD
print(res)