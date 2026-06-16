from copy import copy


def bubble_sort(org_A):
    A = copy(org_A)
    for i in range(len(A)):
        for j in range(len(A) - 1, i, -1):
            if int(A[j][1]) < int(A[j - 1][1]):
                A[j], A[j - 1] = A[j - 1], A[j]
    return A


def selection_sort(org_A):
    A = copy(org_A)
    n = len(A)
    for i in range(n):
        mini = i
        for j in range(i, n):
            if int(A[j][1]) < int(A[mini][1]):
                mini = j
        if mini != i:
            A[i], A[mini] = A[mini], A[i]
    return A

n = int(input())
A = input().split()
B = bubble_sort(A)
C = selection_sort(A)
print(' '.join(B))
print('Stable')
print(' '.join(C))
if B == C:
    print('Stable')
else:
    print('Not stable')

