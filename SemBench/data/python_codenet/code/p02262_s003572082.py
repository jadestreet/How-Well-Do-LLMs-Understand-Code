count = 0
m = 0
G = []
def insertionSort(A, n, g):
    global count
    for i in range(g,n):
        v = A[i]
        j = i - g
        while j >= 0 and A[j] > v:
            A[j+g] = A[j]
            j = j - g
            count += 1
        A[j+g] = v

def shellSort(A, n):
    global count
    global m
    global G
    count = 0
    g = 1
    while g <= n:
        G.append(g)
        g = 3*g + 1
    G.reverse()
    m = len(G)
    for g in G:
        insertionSort(A, n, g)
A = []
n = int(input())
for _ in range(n):
    A.append(int(input()))

shellSort(A,n)

print(m)
print(" ".join(map(str, G)))
print(count)
for a in A:
    print(a)   
    

