class AVLtree:
    """
    参考：http://www.nct9.ne.jp/m_hiroi/light/pyalgo12.html
    insert : 挿入
    erase : 削除
    lower_bound(x) : x <= v なる最小のv、なければ-float("inf")、最小値はlower(-float("inf"))
    upper_bound(x) : v < x なる最大のv、なければfloat("inf")、最大値はupper(float("inf"))
    print(avltree) : デバッグ用
    """
 
    def __init__(self):
        self.root = None
        self.num = 0
        
    def insert(self, x):
        if self.root is None:
            self.root = Node(x)
            self.num += 1
            return
        q = []
        node = self.root
        while True:
            if node.val == x:
                return
            elif x < node.val:
                q.append((node, 1))
                if node.left is None:
                    node.left = Node(x)
                    break
                node = node.left
            else:
                q.append((node, -1))
                if node.right is None:
                    node.right = Node(x)
                    break
                node = node.right
        self.num += 1
        
        # バランス調整
        new_node = None
        while q:
            node, key = q.pop()
            node.bal += key
            node.size += 1
            bal = node.bal
            if not bal:
                while q:
                    node, key = q.pop()
                    node.size += 1
                return
            if bal == 2:
                if node.left.bal == -1:
                    node.left = node.left._rotateL()
                    new_node = node._rotateR()
                    new_node._update_bal()
                else:
                    new_node = node._rotateR()
                    new_node.bal = 0
                    node.bal = 0
                break
            elif bal == -2:
                if node.right.bal == 1:
                    node.right = node.right._rotateR()
                    new_node = node._rotateL()
                    new_node._update_bal()
                else:
                    new_node = node._rotateL()
                    new_node.bal = 0
                    node.bal = 0
                break
        if q:
            node, key = q.pop()
            node.size += 1
            if key == 1:
                node.left = new_node
            else:
                node.right = new_node
        elif new_node is not None:
            self.root = new_node
        while q:
            node, key = q.pop()
            node.size += 1

            
    def erase(self, x):
        if self.root is None:
            return
        q = []
        node = self.root
        while node is not None:
            if node.val == x:
                break
            if x < node.val:
                q.append((node, 1))
                node = node.left
            else:
                q.append((node, -1))
                node = node.right
        else:
            return

        self.num -= 1
        if node.left is not None and node.right is not None:
            q.append((node, -1))
            min_node = node.right
            while min_node.left is not None:
                q.append((min_node, 1))
                min_node = min_node.left
            node.val = min_node.val
            node = min_node
        if q:
            pre, key = q[-1]
        else:
            pre = None
        if node.left is None:
            cnode = node.right
        else:
            cnode = node.left
        if pre is None:
            self.root = cnode
            return
        if key == 1:
            pre.left = cnode
        else:
            pre.right = cnode
        
        # バランス調整
        while q:
            new_node = None
            node, key = q.pop()
            node.bal -= key
            node.size -= 1
            bal = node.bal
            if bal == 2:
                if node.left.bal == -1:
                    node.left = node.left._rotateL()
                    new_node = node._rotateR()
                    new_node._update_bal()
                else:
                    new_node = node._rotateR()
                    if not new_node.bal:
                        new_node.bal = -1
                        node.bal = 1
                    else:
                        new_node.bal = 0
                        node.bal = 0
            elif bal == -2:
                if node.right.bal == 1:
                    node.right = node.right._rotateR()
                    new_node = node._rotateL()
                    new_node._update_bal()
                else:
                    new_node = node._rotateL()
                    if not new_node.bal:
                        new_node.bal = 1
                        node.bal = -1
                    else:
                        new_node.bal= 0
                        node.bal = 0
            elif bal:
                break
            if new_node is not None:
                if not q:
                    self.root = new_node
                    return
                node, key = q[-1]
                if key == 1:
                    node.left = new_node
                else:
                    node.right = new_node
                if new_node.bal:
                    break
        while q:
            node, key = q.pop()
            node.size -= 1
                    
    def lower_bound(self, x):
        res = float("inf")
        node = self.root
        while node is not None:
            if x <= node.val:
                res = node.val
                node = node.left
            else:
                node = node.right
        return res
    
    
    def upper_bound(self, x):
        res = -float("inf")
        node = self.root
        while node is not None:
            if x <= node.val:
                node = node.left
            else:
                res = node.val
                node = node.right
        return res
    
    def __len__(self):
        return self.num

    def __getitem__(self, key):
        if key < 0:
            key += self.num
        key += 1
        node = self.root
        while True:
            idx = node.left.size + 1 if node.left is not None else 1
            if idx <= key:
                key -= idx
                if not key:
                    break
                node = node.right
            else:
                node = node.left
        return node.val

    
    def __str__(self):
        if self.root is None:
            return "[]"
        buff = "["
        for x in self.root._dfs():
            buff += str(x)+", "
        buff = buff.rstrip(", ")
        buff += "]"
        return buff


class Node:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None
        self.bal = 0 #1:左1, -1:右1
        self.size = 1
    
    def _rotateR(self):
        nodeL = self.left
        nodeLL_size = nodeL.left.size if nodeL.left is not None else 0
        nodeR_size = self.right.size if self.right is not None else 0
        self.size -= nodeLL_size + 1
        nodeL.size += nodeR_size + 1
        self.left = nodeL.right
        nodeL.right = self
        return nodeL
    
    
    def _rotateL(self):
        nodeR = self.right
        nodeRR_size = nodeR.right.size if nodeR.right is not None else 0
        nodeL_size = self.left.size if self.left is not None else 0
        self.size -= nodeRR_size + 1
        nodeR.size += nodeL_size + 1
        self.right = nodeR.left
        nodeR.left = self
        return nodeR
    
    
    def _update_bal(self):
        if self.bal == 1:
            self.right.bal = -1
            self.left.bal = 0
        elif self.bal == -1:
            self.right.bal = 0
            self.left.bal = 1
        else:
            self.right.bal = 0
            self.left.bal = 0
        self.bal = 0
    
    
    def _dfs(self):
        if self is not None:
            if self.left is not None:
                for x in self.left._dfs():
                    yield x
            yield self.val
            if self.right is not None:
                for x in self.right._dfs():
                    yield x
                    

n,q = map(int, input().split())
e = []
for i in range(n):
  s,t,x = map(int, input().split())
  e.append((s-x,x,i))
  e.append((t-x,x,i))
e.sort(key=lambda x:x[0])
D = [int(input()) for _ in range(q)]
avl = AVLtree()
ans = []
f = [0]*n
j = 0
N = 2*n
for d in D:
  while j < N and e[j][0] <= d:
    _,x,i = e[j]
    if f[i]:
      avl.erase((x,i))
    else:
      avl.insert((x,i))
      f[i] = 1
    j += 1
  m = avl.lower_bound((-float("inf"),0))
  ans.append(m[0] if m != float("inf") else -1)

for i in ans:
  print(i)
