import sys
input = sys.stdin.readline

def get_sieve_of_eratosthenes(n):
    if not isinstance(n, int):
        raise TypeError('n is int type.')
    if n < 2:
        raise ValueError('n is more than 2')
    prime = [2]
    limit = int(n**0.5) #ルートn以上で割れることはない
    data = [i + 1 for i in range(2, n, 2)] #最初から3スタートの奇数にしておく
    while True:
        p = data[0]
        if limit < p: #ここでイコールが入るとlimitが素数の時にlimit^2が残ってダメ。
            return prime + data
        prime.append(p) #ここで一番最初に取り出した素数を加える。
        data = [e for e in data if e % p != 0] #残りでその素数で割れない数字を取得。

MAX = pow(10,6)
#L = get_sieve_of_eratosthenes(MAX)

def factorization(n):
    arr = []
    temp = n
    if temp%2 == 0:
      cnt = 0
      while temp%2 == 0:
        cnt += 1
        temp//=2
      arr.append(2)
    for i in range(3, int(-(-n**0.5//1))+1,2):
        if temp%i==0:
            cnt=0
            while temp%i==0:
                cnt+=1
                temp //= i
            arr.append(i)
 
    if temp!=1:
        arr.append(temp)
 
    return arr

#XX = factorization(121)
#print(XX)
import math
N = int(input())
A = list(map(int,input().split()))
GCD = math.gcd(A[0],A[1])
for i in range(2,N):
  GCD = math.gcd(GCD,A[i])
  if GCD == 1:
    break
if GCD != 1:
  print("not coprime")
  exit()
A.sort()
SET = set([])
for x in A:
  SL = factorization(x)
  for yakusu in SL:
    if yakusu not in SET:
      SET.add(yakusu)
    else:
      print("setwise coprime")
      exit()
print("pairwise coprime")