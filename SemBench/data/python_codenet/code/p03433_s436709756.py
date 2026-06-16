import sys
def input(): return sys.stdin.readline().strip()

def resolve():
    def main():
        n=int(input())
        a=int(input())
        for i in range(21):
            for j in range(a+1):
                if 500*i+1*j==n:
                    return 'Yes'
        return 'No'
    print(main())
resolve()