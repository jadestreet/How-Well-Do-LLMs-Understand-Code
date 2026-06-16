from random import choice

class dice:
    def __init__(self, X):
        self.x = [0] * 6
        self.x[0] = X[0]
        self.x[1] = X[1]
        self.x[2] = X[2]
        self.x[3] = X[3]
        self.x[4] = X[4]
        self.x[5] = X[5]

    def roll(self, d):
        if d == 'S':
            self.x[0], self.x[1], self.x[2], self.x[3], self.x[4], self.x[5] = \
            self.x[4], self.x[0], self.x[2], self.x[3], self.x[5], self.x[1]
        elif d == 'E':
            self.x[0], self.x[1], self.x[2], self.x[3], self.x[4], self.x[5] = \
            self.x[3], self.x[1], self.x[0], self.x[5], self.x[4], self.x[2]
        elif d == 'W':
            self.x[0], self.x[1], self.x[2], self.x[3], self.x[4], self.x[5] = \
            self.x[2], self.x[1], self.x[5], self.x[0], self.x[4], self.x[3]
        elif d == 'N':
            self.x[0], self.x[1], self.x[2], self.x[3], self.x[4], self.x[5] = \
            self.x[1], self.x[5], self.x[2], self.x[3], self.x[0], self.x[4]

X = list(map(int, input().split()))
n = int(input())
dice1 = dice(X)
distances = ['S', 'E', 'W', 'N']
for i in range(n):
    x1, x2 = map(int, input().split())
    while True:
        d = choice(distances)
        dice1.roll(d)
        if dice1.x[0] == x1 and dice1.x[1] == x2:
            print(dice1.x[2])
            break
