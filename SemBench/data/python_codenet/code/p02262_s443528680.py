import math

cnt = 0

def insertionSort(A,n,g):
    global cnt
    for i in range(g,n):
        v = A[i]
        j = i - g
        while j >= 0 and A[j] > v:
            A[j+g] = A[j]
            cnt += 1
            j -= g
        A[j+g] = v

def shellSort(A, n):
    g = int(n/2) + 1
    G = []
        
    while g > 0:
        G.append(g)
        insertionSort(A, n, g)
        g = int(g/2)
    
    return G

n = int(input())
A = []
for _ in range(n):
    A.append(int(input()))
G = shellSort(A,n)

print(len(G))
print(" ".join(map(str, G)))
print(cnt)
for i in A:
    print(i)
