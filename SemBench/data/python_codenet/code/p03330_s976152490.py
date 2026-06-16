import sys

#+++++

def naiseki(va,vb):
	return sum([a*b for a,b in zip(va,vb)])

def main():
	n , c = map(int, input().split())
		
	ccc=[0]*c
	for i in range(c):
		ccc[i]=[0]*c
	for i in range(c):
		temp=list(map(int,input().split()))
		#ccc[i]=temp
		for j,v in enumerate(temp):
			ccc[j][i]=v
		
	pa(ccc)
		
	ddl=[0,0,0]
	for i in range(3):
		ddl[i]=[0]*c
		
	for i in range(1,n+1):
		ll=list(map(int, input().split()))
		for j, color_v in enumerate(ll,start=1):
			group=(i+j)%3
			ddl[group][color_v-1]+=1
			
	pa('_____ddl_____')
	for i in range(3):
		pa(ddl[i])
		
	rrb=[0]*3
	for i in range(3):
		rrb[i]=[0]*c	
		for j in range(c):
			rrb[i][j]=(naiseki(ddl[i], ccc[j]),j)
			
	pa('____rrb_____')
	for i in range(3):
		pa(rrb[i])
	
	c=[0]	* 3
	for i in range(3):
		rrb[i].sort()
		aa=rrb[i][:3]
		c[i]=aa
		
	pa('____ c _____')
	for i in range(3):
		pa(c[i])
		
	mm=None
	for i in range(3):
		for j in range(3):
			for k in range(3):
				ii=c[0][i][1]
				ji=c[1][j][1]
				ki=c[2][k][1]
				if ii !=ji and ji!=ki and ki!=ii:
					temp=c[0][i][0]+c[1][j][0]+c[2][k][0]
					#pa(temp)
					mm = temp if mm is None else min(mm,temp)
					
	return mm
	
	
#+++++
isTest=False

def pa(v):
	if isTest:
		print(v)

if __name__ == "__main__":
	if sys.platform =='ios':
		sys.stdin=open('inputFile.txt')
		isTest=True
	else:
		pass
		#input = sys.stdin.readline
			
	ret = main()
	if ret is not None:
		print(ret)