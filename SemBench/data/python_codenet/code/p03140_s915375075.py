N = int(input())
A = input()
B = input()
C = input()

answer = A
def calc_answer(answer):
    answer = answer
    for i in range(N):
        ver = [A[i], B[i], C[i]]
        same_index = get_same_index(ver)
        if same_index == (1,2):
            answer_lis = list(answer)
            answer_lis[i] = B[i]
            answer = ''
            for k in answer_lis:
                answer += k
    return answer

def get_same_index(lis):
    if lis[0] == lis[1] == lis[2]:
        return 0, 1, 2
    if lis[0] == lis[1]:
        return 0, 1
    if lis[1] == lis[2]:
        return 1, 2
    if lis[2] == lis[0]:
        return 0, 2
    else:
        return -1


def get_differency(answer):
    differency = 0
    answer = calc_answer(answer)
    for i in range(N):
        if answer[i] != A[i]:
            differency += 1
        if answer[i] != B[i]:
            differency += 1
        if answer[i] != C[i]:
            differency += 1
    return differency

differency = get_differency(answer)
print(differency)