from logging import *
basicConfig(level=DEBUG, format='%(levelname)s: %(message)s')
disable(CRITICAL)

MOD = 10**9 + 7
INF = MOD
def mmul(a, b): return a*b%MOD

n, k = map(int, input().split())
A = [*map(int, input().split())]
P, M = [], [] # plus, minus
for a in A:
    if a < 0: M.append(a)
    else: P.append(a)

debug('A {}'.format(sorted(A, reverse=True, key=lambda x:abs(x))))


def mix():
    len_p = len(P); len_m = len(M)

    P.sort(reverse=True); M.sort()
    P.append(-1); M.append( 1) # add endpoint

    debug('P {}'.format(P));debug('M {}'.format(M))

    pa, ma = [], []
    while len(pa) + len(ma) < k:
        if P[len(pa)] < -M[len(ma)]: ma.append(M[len(ma)])
        else: pa.append(P[len(pa)])

    debug('pa {}'.format(pa));debug('ma {}'.format(ma))
    if len(ma)%2 == 0: return pa + ma

    exist_pa = len(pa) > 0; exist_ma = len(ma) > 0
    remain_p = len_p - len(pa) > 0; remain_m = len_m - len(ma) > 0
    debug('exist_pa {}'.format(exist_pa));debug('exist_ma {}'.format(exist_ma))
    debug('remain_p {}'.format(remain_p));debug('remain_m {}'.format(remain_m))

    if exist_pa & exist_ma & remain_p & remain_m:
        p_in = pa[-1]; p_out = P[len(pa)]
        m_in = ma[-1]; m_out = M[len(ma)]
        if abs(p_in*p_out) < abs(m_in*m_out): pa.pop(); ma.append(m_out)
        else: ma.pop(); pa.append(p_out)
        debug('pa {}'.format(pa));debug('ma {}'.format(ma))
        return pa + ma

    # if (not exist_pa) & exist_ma & remain_p & (not remain_m):
    # if exist_ma & remain_p & (not remain_m):
    if exist_ma & remain_p:
        m_in = ma[-1]; p_out = P[len(pa)]
        ma.pop(); pa.append(p_out)
        debug('pa {}'.format(pa));debug('ma {}'.format(ma))
        return pa + ma

    # if exist_pa & (not exist_ma) & (not remain_p) & remain_m:
    # if exist_pa & (not remain_p) & remain_m:
    if exist_pa & remain_m:
        p_in = pa[-1]; m_out = M[len(ma)]
        pa.pop(); ma.append(m_out)
        debug('pa {}'.format(pa));debug('ma {}'.format(ma))
        return pa + ma

    # --------------------------------
    P.pop(); M.pop()

    P.sort(); M.sort(reverse=True)
    P.append(-1); M.append( 1) # add endpoint
    debug('---')
    debug('P {}'.format(P));debug('M {}'.format(M))

    pa, ma = [], []
    while len(pa) + len(ma) < k:
        if P[len(pa)] >= -M[len(ma)]: ma.append(M[len(ma)])
        else: pa.append(P[len(pa)])

    debug('pa {}'.format(pa));debug('ma {}'.format(ma))
    if len(ma)%2 == 1: return pa + ma

    exist_pa = len(pa) > 0; exist_ma = len(ma) > 0
    remain_p = len_p - len(pa) > 0; remain_m = len_m - len(ma) > 0
    debug('exist_pa {}'.format(exist_pa));debug('exist_ma {}'.format(exist_ma))
    debug('remain_p {}'.format(remain_p));debug('remain_m {}'.format(remain_m))

    if exist_pa & exist_ma & remain_p & remain_m:
        p_in = pa[-1]; p_out = P[len(pa)]
        m_in = ma[-1]; m_out = M[len(ma)]
        if abs(p_in*p_out) >= abs(m_in*m_out): pa.pop(); ma.append(m_out)
        else: ma.pop(); pa.append(p_out)
        debug('pa {}'.format(pa));debug('ma {}'.format(ma))
        return pa + ma

    # if (not exist_pa) & exist_ma & remain_p & (not remain_m):
    if exist_ma & remain_p:
        m_in = ma[-1]; p_out = P[len(pa)]
        ma.pop(); pa.append(p_out)
        debug('pa {}'.format(pa));debug('ma {}'.format(ma))
        return pa + ma

    # if exist_pa & (not exist_ma) & (not remain_p) & remain_m:
    if exist_pa & remain_m:
        p_in = pa[-1]; m_out = M[len(ma)]
        pa.pop(); ma.append(m_out)
        debug('pa {}'.format(pa));debug('ma {}'.format(ma))
        return pa + ma

    # return [0]
    return pa + ma


ans = 1
if k==n:
    debug('k==n: {} == {} '.format(k,n))
    debug('A {}'.format(A))
    for a in A: ans = mmul(ans, a)
else:
    debug('k<n: {} < {} '.format(k,n))
    if len(P) == n:
        debug('n({}) all plus({})'.format(n,len(P)))
        P.sort(reverse=True)
        debug('P[:k] {}'.format(P[:k]))
        for a in P[:k]: ans = mmul(ans, a)
    elif len(M) == n:
        debug('n({}) all minus({})'.format(n,len(M)))
        if k%2:
            debug('k({}) is odd ({})'.format(k,k%2))
            M.sort(reverse=True)
        else:
            debug('k({}) is even ({})'.format(k,k%2))
            M.sort()
        debug('M[:k] {}'.format(M[:k]))
        for a in M[:k]: ans = mmul(ans, a)
    else:
        debug('n({}) mix plus({}):minus({})'.format(n,len(P),len(M)))
        for a in mix(): ans = mmul(ans, a)

ans += MOD; ans %= MOD
debug('ans {}'.format(ans))
print(ans)
