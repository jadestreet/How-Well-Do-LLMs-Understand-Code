MOD = 998244353
MAX = int(2e5 + 5)

fact = [0] * MAX
invFact = [0] * MAX


def bigmod(a, b):
	if b == 0:
		return 1
	ret = bigmod(a, b // 2)
	ret = (ret * ret) % MOD
	if b % 2 == 1:
		ret = (ret * a) % MOD
	return ret


def mod_inverse(a):
	return bigmod(a, MOD - 2)


def pre():
	global fact, invFact
	fact[0] = 1
	for i in range(1, MAX):
		fact[i] = (fact[i - 1] * i) % MOD
	invFact[MAX - 1] = mod_inverse(fact[MAX - 1])
	for i in range(MAX - 2, -1, -1):
		invFact[i] = (invFact[i + 1] * (i + 1)) % MOD


def ncr(nn, rr):
	if nn < 0 or nn < rr or rr < 0:
		return 0
	return (fact[nn] * invFact[rr] * invFact[nn - rr]) % MOD



pre()
n, m, k = map(int, input().split())


ans = 0
for i in range(k + 1):
	ans = (ans + m * bigmod(m - 1, n - 1 - i) * ncr(n - 1, i) ) % MOD

print(ans)
