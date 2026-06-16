def main():
    N = int(input())
    L = len(str(N))
    cand = []
    def dfs(s,N,cand):
        if s != '' and int(s) > N:
            return
        
        for i in ['3','5','7']:
            tmp = s + i
            if int(tmp) <= N:
                cand.append(tmp)
            dfs(tmp,N,cand)
    
    dfs('',N,cand)
    ans = 0
    for c in cand:
        if c.count('3') >= 1 and c.count('5') >= 1  and c.count('7') >= 1:
            ans += 1
    print(ans)
if __name__ == "__main__":
    main()