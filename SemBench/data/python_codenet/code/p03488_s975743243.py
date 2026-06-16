import sys
from collections import deque
def input(): return sys.stdin.readline().strip()


def main():
    s = input()
    x, y = map(int, input().split())
    """
    x, y方向独立に考えられることには気づいたけど、その後の遷移が2^N通りで無理だと思い込んでた。。。
    もらうdpで考えれば確かにO(N^2)で片付く。
    """
    C = [deque([]), []]
    direction = 0 # = X
    cnt = 0
    for c in s:
        if c == 'F':
            cnt += 1
            continue
        if c == 'T':
            C[direction].append(cnt)
            cnt = 0
            direction = 1 - direction
    C[direction].append(cnt)
    
    X = [0] * 16001
    if s[0] == 'F':
        start = C[0].popleft()
        X[8000 + start] = 1
    else:
        X[8000] = 1
    for cnt in C[0]:
        X_new = [0] * 16001
        for i in range(16001):
            if 0 <= i - cnt and i + cnt <= 16000:
                X_new[i] = 1 - (1 - X[i - cnt]) * (1 - X[i + cnt])
            elif 0 <= i - cnt:
                X_new[i] = X[i - cnt]
            else:
                X_new[i] = X[i + cnt]
        X = X_new

    Y = [0] * 16001
    Y[8000] = 1
    for cnt in C[1]:
        Y_new = [0] * 16001
        for i in range(16001):
            if 0 <= i - cnt and i + cnt <= 16000:
                Y_new[i] = 1 - (1 - Y[i - cnt]) * (1 - Y[i + cnt])
            elif 0 <= i - cnt:
                Y_new[i] = Y[i - cnt]
            else:
                Y_new[i] = Y[i + cnt]
        Y = Y_new
    
    if X[8000 + x] == 1 and Y[8000 + y] == 1:
        print("Yes")
    else:
        print("No")

    


if __name__ == "__main__":
    main()
