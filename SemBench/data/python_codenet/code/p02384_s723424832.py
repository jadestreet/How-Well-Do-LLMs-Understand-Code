class Dice:
    def __init__(self,num):
        self.top = num[0]
        self.front = num[1]
        self.right = num[2]
        self.left = num[3]
        self.back = num[4]
        self.bottom = num[5]

    def south_direction(self):
        front = self.top
        bottom = self.front
        back = self.bottom
        top = self.back
        right = self.right
        left = self.left
        
        self.top = top
        self.front = front
        self.bottom = bottom
        self.back = back
        self.right = right
        self.left = left

    def north_direction(self):
        back = self.top
        top = self.front
        front = self.bottom
        bottom = self.back
        right = self.right
        left = self.left
        
        self.top = top
        self.front = front
        self.bottom = bottom
        self.back = back
        self.right = right
        self.left = left

    def east_direction(self):
        right = self.top
        front = self.front
        left = self.bottom
        back = self.back
        bottom = self.right
        top = self.left
        
        self.top = top
        self.front = front
        self.bottom = bottom
        self.back = back
        self.right = right
        self.left = left
        
    def west_direction(self):
        left = self.top
        front = self.front
        right = self.bottom
        back = self.back
        top = self.right
        bottom = self.left
        
        self.top = top
        self.front = front
        self.bottom = bottom
        self.back = back
        self.right = right
        self.left = left
    
    def clockwise_rotate(self):
        top = self.top
        left = self.front
        bottom = self.bottom
        right = self.back
        front = self.right
        back = self.left
        
        self.top = top
        self.front = front
        self.bottom = bottom
        self.back = back
        self.right = right
        self.left = left
        
    
    def print_top(self):
        print(self.top)

    def judge_right(self, top, front):
        while True:
            if self.top == top and self.front == front:
                print(self.right)
                break
            elif top==self.front:
                self.north_direction()
            elif top == self.left:
                self.east_direction()
            elif top == self.back:
                self.south_direction()
            elif top == self.right:
                self.west_direction()
            elif top == self.bottom:
                self.north_direction()
                self.north_direction()
        
            elif front == self.front:
                pass
            elif front == self.left:
                self.clockwise_rotate()
                self.clockwise_rotate()
                self.clockwise_rotate()
            elif front == self.back:
                self.clockwise_rotate()
                self.clockwise_rotate()
            elif front == self.right:
                self.clockwise_rotate()
    
num = list(map(int,input().split()))
rep=int(input())
d = Dice(num)

for i in range(rep):
    top, front = map(int, input().split())
    d.judge_right(top, front)
