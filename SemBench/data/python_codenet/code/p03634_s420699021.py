import sys
import os
from collections import defaultdict
adj = defaultdict(list)
vis =[0 for i in range(1000000)]
dis =[0 for i in range(1000000)]
# since it's a tree shortest path will be only one and unique between two node
# find distance from k to each and every node 
def dfs(u, p):
	for v, w in adj[u]:
		if v==p:
			continue
		dis[v]=dis[u]+w
		dfs(v, u)

def main():
	n = int(input())
	for i in range(n-1):
		a, b, w = map(int , input().split())
		adj[a].append((b, w))
		adj[b].append((a, w))

	q, k = map(int , input().split())
	sys.setrecursionlimit(1000000)
	dfs(k , 0)
	for i in range(q):
		x, y  =map(int , input().split())
		# print the sum of the two distance from k 
		print(dis[x]+dis[y])
#	rec_limit= sys.getrecursionlimit()
#	print(rec_limit)


if __name__ == "__main__":
	main()