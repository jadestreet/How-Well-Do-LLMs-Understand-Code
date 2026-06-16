class Dice:
    def __init__(self, eyes):
        self._eyes = ['dummy'] + eyes

    @property
    def eye(self):
        return self._eyes[1]

    def roll(self, direction):
        old = self._eyes
        new = ['dummy'] * 7
        if direction == 'N':
            new[1] = old[2]
            new[2] = old[6]
            new[3] = old[3]
            new[4] = old[4]
            new[5] = old[1]
            new[6] = old[5]
        elif direction == 'S':
            new[1] = old[5]
            new[2] = old[1]
            new[3] = old[3]
            new[4] = old[4]
            new[5] = old[6]
            new[6] = old[2]
        elif direction == 'W':
            new[1] = old[3]
            new[2] = old[2]
            new[3] = old[6]
            new[4] = old[1]
            new[5] = old[5]
            new[6] = old[4]
        elif direction == 'E':
            new[1] = old[4]
            new[2] = old[2]
            new[3] = old[1]
            new[4] = old[6]
            new[5] = old[5]
            new[6] = old[3]
        else:
            raise ValueError('NEWS箱推し')
        self._eyes = new


eyes = input().split()
dice = Dice(eyes)

direction_text = input()
for d in direction_text:
    dice.roll(d)

print(dice.eye)

