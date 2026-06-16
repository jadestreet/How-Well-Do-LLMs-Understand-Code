class SegTree():
    def segFunc(self, x, y):
        return x+y
    def searchIndexFunc(self, val):
        return True
    def __init__(self, ide, init_val):
        n = len(init_val)
        self.ide_ele = ide
        self.num = 2**(n-1).bit_length()
        self.seg = [self.ide_ele] * 2 * self.num
        for i in range(n):
            self.seg[i+self.num-1] = init_val[i]    
        for i in range(self.num-2,-1,-1):
            self.seg[i] = self.segFunc(self.seg[2*i+1],self.seg[2*i+2])
    def update(self, idx, val):
        idx += self.num-1
        self.seg[idx] = val
        while idx:
            idx = (idx-1)//2
            self.seg[idx] = self.segFunc(self.seg[idx*2+1], self.seg[idx*2+2])
    def addition(self, idx, val):
        idx += self.num-1
        self.seg[idx] += val
        while idx:
            idx = (idx-1)//2
            self.seg[idx] = self.segFunc(self.seg[idx*2+1], self.seg[idx*2+2])
    def multiplication(self, idx, val):
        idx += self.num-1
        self.seg[idx] *= val
        while idx:
            idx = (idx-1)//2
            self.seg[idx] = self.segFunc(self.seg[idx*2+1], self.seg[idx*2+2])
    def query(self, begin, end):
        if end <= begin:
            return self.ide_ele
        begin += self.num-1
        end += self.num-2
        res = self.ide_ele
        while begin + 1 < end:
            if begin&1 == 0:
                res = self.segFunc(res, self.seg[begin])
            if end&1 == 1:
                res = self.segFunc(res, self.seg[end])
                end -= 1
            begin = begin//2
            end = (end-1)//2
        if begin == end:
            res = self.segFunc(res, self.seg[begin])
        else:
            res = self.segFunc(self.segFunc(res, self.seg[begin]), self.seg[end])
        return res
    def getLargestIndex(self, begin, end):
        L, R = begin, end
        if not self.searchIndexFunc(self.query(begin, end)):
            return None
        while L+1 < R:
            P = (L+R)//2
            if self.searchIndexFunc(self.query(P, R)):
                L = P
            else:
                R = P
        return L
    def getSmallestIndex(self, begin, end):
        L, R = begin, end
        if not self.searchIndexFunc(self.query(begin, end)):
            return None
        while L+1 < R:
            P = (L+R+1)//2
            if self.searchIndexFunc(self.query(L, P)):
                R = P
            else:
                L = P
        return L

def main():
    n = int(input())
    s = input()
    alp = [[0]*n for _ in range(26)]
    for i, c in enumerate(s):
        alp[ord(c) - ord("a")][i] = 1
    seg = [SegTree(0, alp[i]) for i in range(26)]
    q = int(input())
    ans = []
    for _ in range(q):
        a, b, c = map(str, input().split())
        if a == "1":
            b = int(b) - 1
            for i in range(26):
                if alp[i][b] == 1:
                    alp[i][b] = 0
                    seg[i].update(b, 0)
            alp[ord(c) - ord("a")][b] = 1
            seg[ord(c) - ord("a")].update(b, 1)
        else:
            b, c = int(b)-1, int(c)
            cnt = 0
            for i in range(26):
                if seg[i].query(b, c) > 0:
                    cnt += 1
            ans.append(cnt)
    for v in ans:
        print(v)

if __name__ == "__main__":
    main()