import sys
n = int(input())
sort_list = list(map(int,input().split()))

cnt = []
def merge(A, left,mid,right):
    n1 = mid -left
    n2 = right - mid
    L = [i for i in A[left : left + n1]]
    R = [i for i in A[mid : mid + n2]]
    L.append(sys.maxsize)
    R.append(sys.maxsize)

    i = 0
    j = 0
    c = 0
    for k in range(left,right):
        if L[i] <= R[j]:
            A[k] = L[i]
            i = i + 1
        else:
            A[k] = R[j]
            j = j + 1
        c += 1

    cnt.append(c)

def mergesort(A,left,right):
    if left + 1 < right:
        mid = (left + right) // 2
        mergesort(A,left,mid)
        mergesort(A,mid,right)
        merge(A,left,mid,right)

mergesort(sort_list, 0, len(sort_list))
print(' '.join([str(i) for i in sort_list]))
print(sum(cnt))

