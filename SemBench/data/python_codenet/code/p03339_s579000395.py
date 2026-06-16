import sys
def input(): return sys.stdin.readline().strip()


def main():
    N = int(input())
    S = input()
    east = [0] * (N + 1)
    west = [0] * (N + 1)
    for i in range(1, N + 1):
        if S[i - 1] == "W":
            west[i] = west[i - 1] + 1
        else:
            west[i] = west[i - 1]
    for i in range(N - 1, -1, -1):
        if S[i] == "E":
            east[i] = east[i + 1] + 1
        else:
            east[i] = east[i + 1]

    ans = 10**18
    for n in range(N):
        ans = min(ans, west[n] + east[n + 1])
    print(ans)



if __name__ == "__main__":
    main()
