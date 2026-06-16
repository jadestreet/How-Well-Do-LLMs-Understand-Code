def get_caps(a):
  dic = dict()

  for ai in a:
    dic.setdefault(ai, 0)
    dic[ai] += 1

  return dic


def is_match(caps):
  global N

  if 0 in caps.keys():
    if caps[0] == N:
      return True
  
  if N % 3 == 0:
    if 0 in caps.keys() and len(caps) == 2:
      if caps[0] == N//3:
        return True
    elif len(caps) == 3:
      x, y, z = caps.keys()
    
      if x ^ y ^ z == 0:
        if caps[x] == caps[y] == caps[z] == N//3:
          return True


# A - XOR Circle
N = int(input())
a = list(map(int, input().split()))

# 帽子の情報をdictに入れる
caps = get_caps(a)

if is_match(caps):
  print('Yes')
else:
  print('No')