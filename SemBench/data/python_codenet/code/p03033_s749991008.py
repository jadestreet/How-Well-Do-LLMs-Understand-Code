def main():
    import sys
    input = sys.stdin.readline

    n, q = map(int, input().split())

    stx = []
    tmp = set([])

    for _ in range(n):
        s,t,x = map(int, input().split())
        stx.append((s,t,x))
        tmp.add(x-t)
        tmp.add(x-s)

    d = {}
    for i in range(q):
        di = -int(input())
        tmp.add(di)
        d[di] = i

    stx.sort(key = lambda x:x[2])

    v2i = {}

    for i, v in enumerate(sorted(tmp)):
        v2i[v] = i

    l = [1] * (len(tmp) + 1)

    for di in d:
        l[v2i[di]] = di
            

    #####単位元######
    ide_ele_min = 1

    #num_min:n以上の最小の2のべき乗
    N = len(l)

    num_min =2**(N-1).bit_length()
    seg_min=[ide_ele_min]*2*num_min

    def init_min(init_min_val):
        #set_val
        for i in range(N):
            seg_min[i+num_min-1]=init_min_val[i]    
        #built
        for i in range(num_min-2,-1,-1) :
            seg_min[i]=min(seg_min[2*i+1],seg_min[2*i+2]) 
    
    def update_min(k,x):
        k += num_min-1
        seg_min[k] = x
        while k:
            k = (k-1)//2
            seg_min[k] = min(seg_min[k*2+1],seg_min[k*2+2])
        
    def query_min(p,q):
        if q<=p:
            return ide_ele_min
        p += num_min-1
        q += num_min-2
        res=ide_ele_min
        while q-p>1:
            if p&1 == 0:
                res = min(res,seg_min[p])
            if q&1 == 1:
                res = min(res,seg_min[q])
                q -= 1
            p = p//2
            q = (q-1)//2
        if p == q:
            res = min(res,seg_min[p])
        else:
            res = min(min(res,seg_min[p]),seg_min[q])
        return res



    init_min(l)
    ans = [-1] * q

    for s, t, x in stx:
        l = v2i[x-t] + 1
        r = v2i[x-s] + 1
        v = query_min(l, r)
        while v != 1:
            i_d = d[v]
            i_sg = v2i[v]
            ans[i_d] = x
            update_min(i_sg, 1)
            v = query_min(l, r)

    for ansi in ans:
        print(ansi)
            
if __name__ == '__main__':
    main()

