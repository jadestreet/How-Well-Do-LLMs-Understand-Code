from collections import defaultdict
from collections import deque
from collections import Counter
import math

def readInt():
	return int(input())
def readInts():
	return list(map(int, input().split()))
def readChar():
	return input()
def readChars():
	return input().split()

n,m = readInts()
mod = 10**9+7
if abs(n-m)>1:
	print(0)
else:
	ans = 1
	for i in range(1,n+1,):
		ans = (ans*(i%mod))%mod
	for i in range(1,m+1):
		ans = (ans*(i%mod))%mod
	if abs(n-m)==0:
		ans = (ans*2)%mod
	print(ans)