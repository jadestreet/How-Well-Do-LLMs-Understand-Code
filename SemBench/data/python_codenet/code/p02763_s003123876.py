#単位元を設定
ide = 0

class SegmentTree:
	def __init__(self,n):
        #セグ木の頂点はindex == 1から。index == 0は無視すること。
        #つまり、STtable[0]は無視。頂点はSTtable[1]。
		self.n = n
		tmp = 0
		while True:
			if 2 ** tmp >= self.n:
				break
			tmp += 1
		self.STtable = [ide] * (2*2**tmp)
		self.STtable_size = len(self.STtable)

	def update(self,i,a):
        #更新のためのインデックスの指定は0_indexedで。
		a_bit = 1 << ord(a)-97
		i += self.STtable_size//2
		self.STtable[i] = a_bit
		while i > 0:
			i //= 2
			self.STtable[i] = self.STtable[i*2] | self.STtable[i*2+1]

	def find(self,a,b,k=1,l=0,r=None):
        #kは頂点番号。初期値は1にすること。
		#[a,b)の最小を返す。
		#[l,r)からです。
        #初期値のrは、self.STtable_size//2にすると、ちょうど要素数と同じ値になって[l,r)のrになる。
        #問題に適するように範囲を指定するように注意。大体[l,r]で指定されている。
		if r == None:
			r = self.STtable_size//2        
		if a >= r or b <= l:
			return ide
		elif a <= l and b >= r:
			return self.STtable[k]
		else:
			mid = (l+r)//2
			if b <= mid:
				return self.find(a,b,2*k,l,mid)
			elif a >= mid:
				return self.find(a,b,2*k+1,mid,r)
			else:
				v1 = self.find(a,mid,2*k,l,mid)
				v2 = self.find(mid,b,2*k+1,mid,r)
			return v1 | v2

N = int(input())
solve = SegmentTree(N)
S = input()
for i in range(N):
	solve.update(i,S[i])
Q = int(input())
ans = []
for _ in range(Q):
	a,b,c = map(str, input().split())
	if a == '1':
		solve.update(int(b)-1,c)
	else:
		tmp = solve.find(int(b)-1,int(c))
		cnt = 0
		for i in range(26):
			if tmp >> i & 1 == 1:
				cnt += 1
		ans.append(cnt)

for a in ans:
	print(a)
