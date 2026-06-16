def i():
	return int(input())
def i2():
	return map(int,input().split())
def s():
	return str(input())
def l():
	return list(input())
def intl():
	return list(int(k) for k in input().split())

n = i()
s = s()

alf = "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ"

for i in range(len(s)):
	for j in range(26):
		if s[i] == alf[j]:
			print(alf[j+n],end="")
			continue