#!/usr/bin/env python3
import sys

MOD = 1000000007  # type: int


def solve(H: int, W: int, K: int):
    if W == 1:
        print(1)
        return 
    ## dp1[i][j] = H=１の時i->jに行く引き方
    ## 4→5と5→4の弾き方は同じ
    dp1 = [[0]*W for _ in range(W)]

    for i in range(2): 
        for j in range(W):
            # tmp[i][0] = iまでの見た時iに線引いてないものの総数
            # tmp[i][1] = iまでの見た時iに線引いているものの総数
            tmp = [[-1]*2 for _ in range(W-1)]
            if i == 0 or j == W-1: ## j -> j
                tmp[0][0] = 1
                if j == 0:
                    tmp[0][1] = 0
                else: ## 両隣にedgeがあってはいけない
                    if j != W-1: tmp[j][1] = 0
                    tmp[j-1][1] = 0
                    if tmp[0][1] != 0: tmp[0][1] = 1

                for k in range(0,W-2):
                    tmp[k+1][0] = tmp[k][0] + tmp[k][1] ## 前の幅に引いてても引いてなくてもいける
                    if tmp[k+1][1] == -1: 
                        tmp[k+1][1] = tmp[k][0] ## 前の幅に引いてない時のみいける。元々zeroが入ってたらパス
                
                dp1[j][j] = sum(tmp[-1])

            else: # j-> j+1
                if j == 0: 
                    tmp[0][1] = 1
                    tmp[0][0] = 0                    
                else:
                    tmp[j][0] = 0 ## jには絶対引いてなくてはならない
                    if j < W-2: tmp[j+1][1] = 0
                    tmp[j-1][1] = 0
                    if tmp[0][1] != 0:
                        tmp[0][1] = 1
                    tmp[0][0] = 1

                for k in range(0,W-2):
                    if tmp[k+1][0] == -1:
                        tmp[k+1][0] = tmp[k][0] + tmp[k][1] ## 前の幅に引いてても引いてなくてもいける
                    if tmp[k+1][1] == -1: 
                        tmp[k+1][1] = tmp[k][0] ## 前の幅に引いてない時のみいける。元々zeroが入ってたらパス
                dp1[j][j+1] = sum(tmp[-1])


    # dp2[h][w] = 高さhのときにw-1にいる弾き方の総数
    dp2 = [[0]*W for _ in range(H+1)]
    dp2[1] = dp1[0]
    for h in range(1,H):
        for k in range(W):
            if k >= 1 and k < W-1:
                dp2[h+1][k] = dp1[k-1][k]*dp2[h][k-1] + dp1[k][k]*dp2[h][k] + dp1[k][k+1]*dp2[h][k+1]
            elif k>=1:
                dp2[h+1][k] = dp1[k-1][k]*dp2[h][k-1] + dp1[k][k]*dp2[h][k]
            elif k <W-1:
                dp2[h+1][k] = dp1[k][k]*dp2[h][k] + dp1[k][k+1]*dp2[h][k+1]


    print(dp2[H][K-1]%MOD)

    return


def main():
    def iterate_tokens():
        for line in sys.stdin:
            for word in line.split():
                yield word
    tokens = iterate_tokens()
    H = int(next(tokens))  # type: int
    W = int(next(tokens))  # type: int
    K = int(next(tokens))  # type: int
    solve(H, W, K)

if __name__ == '__main__':
    main()
