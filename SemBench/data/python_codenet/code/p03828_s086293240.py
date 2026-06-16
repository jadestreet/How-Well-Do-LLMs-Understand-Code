class Factorization:	
	def __init__(self):
		# privateなインスタンス変数を作成
		self.__factors = dict()
		self.__n = 0
	
	
	def get_factors(self, n):
		# [summary] 素因数分解した結果を、辞書([素因数, 指数]...)で返す
		self.__factors.clear()
		self.__n = n
		
		if n < 2:
			# 2より小さい数の場合、素因数分解できない
			return { n:1 }
		else:
			self.__factorization()
			
			return self.__factors
	
	
	def get_divisors(self, n):
		# [summary] 約数をリスト化して返す
		self.__factors.clear()
		self.__n = n
		
		
	def count_divisors(self, n):
		# [summary] 約数の個数を返す
		self.__factors.clear()
		self.__n = n
		
		if n < 2:
			return 1
		else:
			self.__factorization()
			count = 1
			
			for v in self.__factors.values():
				count *= v + 1
			
			return count
	

	def	__factorization(self):
		# [summary]素因数分解した結果を、インスタンス変数に格納
		
		# 2,3,5で、割れなくなるまで割り続ける
		# (末尾に2,3,5のつく数は素数でないことが明白なので
		# 後続の処理で素数のリストに入れないように、先に処理する)
		self.__divide_with(2)
		self.__divide_with(3)
		self.__divide_with(5)
			
		# 平方根以下の素数で総当たりで試し割りする
		# (実際は、素数らしき数)
		import math
		sqrt_ = math.floor(math.sqrt(self.__n))
			
		primes = [7, 11, 13, 17, 19, 23, 29, 31]
		i = 0
		is_break = False
			
		while self.__n > 1:
			for p in primes:
				if p + i <= sqrt_:
					self.__divide_with(p + i)
				else:
					# 試し割りする数が平方根を超えたら、ループを抜ける
					is_break = True
						
					# 1が素因数に追加されることを防止
					if self.__n > 1:
						self.__factors.setdefault(self.__n, 1)
				
			if is_break:
				break
			else:
				i += 30
	
	
	def __divide_with(self, d):
		count = 0
		
		while self.__n % d == 0:
			self.__n //= d
			count += 1
		
		if count > 0:
			self.__factors.setdefault(d, count)


# C - Factors of Factorial
n = int(input())

if n == 1:
	print(1)
else:
	lib = Factorization()
	factors = dict()

	for i in range(2, n + 1):
		for k, v in lib.get_factors(i).items():
			factors.setdefault(k, 0)
			factors[k] += v
	
	ans = 1
	
	for v in factors.values():
		ans = ans * (v + 1) % (10 ** 9 + 7)

	print(ans)