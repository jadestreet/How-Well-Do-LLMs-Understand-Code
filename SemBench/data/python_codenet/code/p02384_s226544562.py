class Dice:
    def __init__(self, top, front, right, left, back, bottom):
        self.TOP = top
        self.BOTTOM = bottom
        self.FRONT = front
        self.BACK = back
        self.LEFT = left
        self.RIGHT = right
    
    def move(self, direction):
        if direction == "N":
            self.move_N()
        elif direction == "E":
            self.move_E()
        elif direction == "S":
            self.move_S()
        elif direction == "W":
            self.move_W()
        elif direction == "SIDE":
            self.move_SIDE()
        else:
            raise Exception
    
    def move_N(self):
        tmp = self.TOP
        self.TOP = self.FRONT
        self.FRONT = self.BOTTOM
        self.BOTTOM = self.BACK
        self.BACK = tmp

    def move_S(self):
        tmp = self.TOP
        self.TOP = self.BACK
        self.BACK = self.BOTTOM
        self.BOTTOM = self.FRONT
        self.FRONT = tmp
        
    def move_W(self):
        tmp = self.TOP
        self.TOP = self.RIGHT
        self.RIGHT = self.BOTTOM
        self.BOTTOM = self.LEFT
        self.LEFT = tmp

    def move_E(self):
        tmp = self.TOP
        self.TOP = self.LEFT
        self.LEFT = self.BOTTOM
        self.BOTTOM = self.RIGHT
        self.RIGHT = tmp
    
    def move_SIDE(self):
        tmp = self.FRONT
        self.FRONT = self.RIGHT
        self.RIGHT = self.BACK
        self.BACK = self.LEFT
        self.LEFT = tmp

def get_right(t, f):
    dice = Dice(top, front, right, left, back, bottom)
    has_top = False
    for _ in range(4):
        dice.move("N")
        if dice.TOP == t:
            has_top = True
            break
    if not has_top:
        for _ in range(4):
            dice.move("E")
            if dice.TOP == t:
                has_top = True
                break
    for _ in range(4):
        dice.move("SIDE")
        if dice.FRONT == f:
            return dice.RIGHT
    
top, front, right, left, back, bottom = map(int,input().split())
dice = Dice(top, front, right, left, back, bottom)
n = int(input())
for _ in range(n):
    t, f = map(int, input().split())
    l = None
    if top == t and front == f:
        r = right
    else:
        r = get_right(t, f)
    print(r)
    
