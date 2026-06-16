import queue
h, w, k = map(int, input().split())
s=[input() for i in range(h)]
ans = [[0]*w for i in range(h)]

def BFS(i, j, count):
  ans[i][j]=str(count)
  movex = [0, 0]
  movey = [1, -1]
  q = queue.Queue()
  q.put([i, j])
  while not q.empty():
    y, x = q.get()
    for i in range(2):
      nx = x+movex[i]
      ny = y+movey[i]
      if 0<=ny<=h-1 and ans[ny][nx]==0 and s[ny][nx]==".":
        ans[ny][nx]=str(count)
        q.put([ny, nx])

def DFS(i, j): 
  movex = [1, -1]
  movey = [0, 0]
  x = j
  y = i
  #右を見る
  while x<=w-1:
    if ans[y][x]==0:
       x+=1
    else:
       return ans[y][x]
  x=j
  while x>=0:
    if ans[y][x]==0:
      x-=1
    else:
      return ans[y][x]

count = 1
for i in range(h):
  for j in range(w):
    if s[i][j]== "#":
      BFS(i, j, count)
      count+=1
  
for i in range(h):
  for j in range(w):
    if ans[i][j]==0:
      ans[i][j]=DFS(i, j)
      
for i in range(h):
  print(" ".join(ans[i]))
