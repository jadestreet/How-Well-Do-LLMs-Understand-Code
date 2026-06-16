# D - Friends
def add_to_graph(A, B):
  global graph

  graph.setdefault(A, [])
  graph[A].append(B)


def add_to_group(p):
  global que
  global group
  global is_finished

  que.append(p)
  group.add(p)
  is_finished[p] = True


from collections import deque

N, M = map(int, input().split())
graph = dict()

for i in range(M):
  A, B = map(int, input().split())
  add_to_graph(A, B)
  add_to_graph(B, A)

# その人を探索したかどうかのフラグ
is_finished = [False] * (N + 1)
groups = []

for i in range(1, N + 1):
  que = deque()
  group = set()

  if not is_finished[i]:
    add_to_group(i)

    while len(que) > 0:
      p = que.popleft()
  
      if p in graph.keys():
        for v in graph[p]:
          if not is_finished[v]:
            add_to_group(v)
    
      groups.append(group)

ans = 0

for g in groups:
  ans = max(ans, len(g))

print(ans)