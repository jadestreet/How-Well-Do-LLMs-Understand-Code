import sys
input=sys.stdin.readline

class list2D:
    def __init__(self, H, W, num):
        self.__H = H
        self.__W = W
        self.__dat = [num] * (H * W)

    def __getitem__(self, a):
        return self.__dat[a[0]*self.__W+a[1]]

    def __setitem__(self, a, b):
        self.__dat[a[0]*self.__W+a[1]] = b

    def debug(self):
        print(self.__dat)

class list3D:
    def __init__(self, H, W, D, num):
        self.__H = H
        self.__W = W
        self.__D = D
        self.__X = W * D
        self.__dat = [num] * (H * W * D)

    def __getitem__(self, a):
        return self.__dat[a[0]*self.__X+a[1]*self.__D + a[2]]

    def __setitem__(self, a, b):
        self.__dat[a[0]*self.__X+a[1]*self.__D + a[2]] = b

    def debug(self):
        print(self.__dat)

def main():
    r,c,k=map(int,input().split())
    v = list2D(r, c, 0)

    for _ in range(k):
        ri,ci,a=map(int,input().split())
        v[ri-1, ci-1] = a

    dp = list3D(r, c, 4, 0)
    #print(dp)
    if v[0, 0]>0: dp[0, 0, 1] = v[0, 0]

    for i in range(r):
        for j in range(c):
            val = v[i, j]
            if i>0:
                x = max(dp[i-1, j, 0], dp[i-1, j, 1], dp[i-1, j, 2], dp[i-1, j, 3])
                dp[i, j, 1]=x+val
                dp[i, j, 0]=x

            if j>0:
                X = dp[i, j-1, 0]
                Y = dp[i, j-1, 1]
                V = dp[i, j-1, 2]
                Z = dp[i, j-1, 3]
                dp[i, j, 0]=max(dp[i, j, 0],X)
                dp[i, j, 1]=max(dp[i, j, 1],X+val,Y)
                dp[i, j, 2]=max(Y+val,V)
                dp[i, j, 3]=max(V+val,Z)

    #print(dp)
    ans=0
    for i in range(4): ans=max(dp[r-1, c-1, i],ans)
    return print(ans)
if __name__=="__main__":
    main()
