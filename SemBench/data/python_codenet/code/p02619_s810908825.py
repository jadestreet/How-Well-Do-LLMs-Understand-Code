import sys, heapq

def calcScores(D, complaints, satisfications, HoldedContestDays):
    TotalSatisfications = [0]
    ContestDays = [1] * 26
    complaint_all = 0
    for i in range(26):
        complaint_all += complaints[i]

    complaint_sum = 0
    for i in range(D):
        complaint_sum += complaint_all
        Contest = HoldedContestDays[i]
        complaint_sum -= ContestDays[Contest] * complaints[Contest]
        ContestDays[Contest] = 0

        satisfication_day_i = TotalSatisfications[-1] + satisfications[i][Contest] - complaint_sum
        TotalSatisfications.append(satisfication_day_i)
        for j in range(26):
            ContestDays[j] += 1
    return TotalSatisfications

def calccontestnumbers(D, complaints, satisfications):
    ContestDays = [1] * 26
    HoldedContests = [-1] * D
    for i in range(D):
        Demands = []
        for j in range(26):
            Demand_j = ContestDays[j] * complaints[j] + satisfications[i][j]
            heapq.heappush(Demands, (-Demand_j, j) )
            ContestDays[j] += 1
        print("Day", i, ":", Demands)
        Demand_Contest = heapq.heappop(Demands)
        Contest = Demand_Contest[1]
        ContestDays[Contest] =1
        HoldedContests[i] = Contest+1
    return HoldedContests



"""
13: 19922, 89
20: 19830, 80

20: 19830 - 80 * 5 = 19430
13: 19922 - 89 * 2 = 19744
毎日1つのコンテスト
満足度をあげるようにコンテスト
ci * (最後にコンテストを行ってからの経過日数)満足度低下
上昇値はs_d_i

"""
if(__name__ == "__main__"):
    D = int(input().strip())
    complaints = list(map(int, input().split() ) )

    satisfications = []
    for i in range(D):
        satisfication = list(map(int, input().split() ) )
        satisfications.append(satisfication)
    HoldedContestDays =[0] * D
    for i in range(D):
        HoldedContestDays[i] = int(input().strip())
        HoldedContestDays[i] -= 1
    Scores = calcScores(D, complaints, satisfications, HoldedContestDays)
    for i in range(D):
        print(Scores[i+1])
