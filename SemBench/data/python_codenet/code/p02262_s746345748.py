def insertionSort(A, n, g):
    cnt = 0
    for i in range(g, n):
        v = A[i]
        j = i - g
        while j >= 0 and A[j] > v:
            A[j+g] = A[j]
            j = j - g
            cnt += 1
        A[j+g] = v
    return cnt


def shellSort(A, n):
    G = []
    h = 1
    while True:
        if h > n:
            break
        G.append(h)
        h = 3 * h + 1

    cnt = 0
    print(len(G))
    G = list(reversed(G))
    for g in G:
        cnt += insertionSort(A, n, g)

    print(*G)
    print(cnt)
    print('\n'.join(map(str, A)))


arr_length = int(input())
arr_num = []
for i in range(arr_length):
    arr_num.append(int(input()))

shellSort(arr_num, arr_length)
