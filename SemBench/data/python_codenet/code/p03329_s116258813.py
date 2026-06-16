import sys
input = sys.stdin.buffer.readline


#sys.setrecursionlimit(10**9)
#from functools import lru_cache

def RD(): return sys.stdin.read()
def II(): return int(input())
def MI(): return map(int,input().split())
def MF(): return map(float,input().split())
def LI(): return list(map(int,input().split()))
def LF(): return list(map(float,input().split()))
def TI(): return tuple(map(int,input().split()))
# rstrip().decode()

def main():
	n=II()
	dp=list(range(10**5+1))
	x=[]
	a=6
	while a<10**5:
		x.append(a)
		a*=6
	a=9
	while a<10**5:
		x.append(a)
		a*=9
	x.sort()
	#print(x)

	#print(dp)

	for i in x:
		for j in range(i,10**5+1):
			dp[j]=min(dp[j],dp[j-i]+1)
	print(dp[n])



if __name__ == "__main__":
	main()
