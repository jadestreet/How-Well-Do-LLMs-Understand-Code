# Python template 
from collections import defaultdict 
import sys
import math 

def get_array(): return list(map(int , sys.stdin.readline().strip().split()))
def get_ints(): return map(int, sys.stdin.readline().strip().split())
def input(): return sys.stdin.readline().strip()

sys.setrecursionlimit(10**6) 

# Python3 program to find the number of pairs 
# such that gcd equals to 1 
N = 1000005

lpf = [0 for i in range(N)] 
mobius = [0 for i in range(N)] 

# Function to calculate least 
# prime factor of each number 
def least_prime_factor(): 

	for i in range(2, N): 

		# If it is a prime number 
		if (lpf[i] == 0): 

			for j in range(i, N, i): 

				# For all multiples which are not 
				# visited yet. 
				if (lpf[j] == 0): 
					lpf[j] = i 

# Function to find the value of Mobius function 
# for all the numbers from 1 to n 
def Mobius(): 

	for i in range(1, N): 

		# If number is one 
		if (i == 1): 
			mobius[i] = 1
		else: 

			# If number has a squared prime factor 
			if (lpf[ (i // lpf[i]) ] == lpf[i]): 
				mobius[i] = 0

			# Multiply -1 with the previous number 
			else: 
				mobius[i] = -1 * mobius[i // lpf[i]] 

# Function to find the number of pairs 
# such that gcd equals to 1 
def gcd_pairs(a, n): 

	# To store maximum number 
	maxi = 0

	# To store frequency of each number 
	fre = [0 for i in range(N)] 

	# Find frequency and maximum number 
	for i in range(n): 
		fre[a[i]] += 1
		maxi = max(a[i], maxi) 

	least_prime_factor() 
	Mobius() 

	# To store number of pairs with gcd equals to 1 
	ans = 0

	# Traverse through the all possible elements 
	for i in range(1, maxi + 1): 
		if (mobius[i] == 0): 
			continue

		temp = 0
		for j in range(i, maxi + 1, i): 
			temp += fre[j] 

		ans += temp * (temp - 1) // 2 * mobius[i] 

	# Return the number of pairs 
	return ans 

# Driver code 

n = int(input())

a = get_array() 
if gcd_pairs(a,n) == (n*(n-1))//2:
    print("pairwise coprime")
else:
    gs = a[0]
    for i in range(1,n):
        gs = math.gcd(gs,a[i])
    if gs == 1:
        print("setwise coprime")
    else:
        print("not coprime")

