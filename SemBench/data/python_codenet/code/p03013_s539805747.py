from itertools import product

def mat2_mul(X, Y):
	z = [[0, 0], [0, 0]]
	for (i, j, k) in product(range(2), range(2), range(2)):
		z[i][j] += X[i][k] * Y[k][j]
	return z

def mat2_pow(X, n):
	if n == 0:
		return [[1, 0], [0, 1]]
	elif n % 2:
		return mat2_mul(X, mat2_pow(X, n - 1))
	else:
		half_pow = mat2_pow(X, n / 2)
		return mat2_mul(half_pow, half_pow)

def fibona(n):
	if n == 0:
		return 0
	else:
		f = [[0, 1], [1, 1]]
	return mat2_pow(f, n - 1)[1][1]

def main():
    n, m = map(int,input().split())
    mlis = []
    for _ in range(m):
        a = int(input())
        mlis.append(a)
    ans = 1
    mae = 0

    infi = 10 ** 9 + 7
    for num in mlis:
        ans *= fibona(num-mae)
        ans %= infi
        mae = num + 1

    nobori = n - mae + 1
    ans *= fibona(nobori) 
    ans %= infi
    print(int(ans))
    



if __name__ == "__main__":
    main()