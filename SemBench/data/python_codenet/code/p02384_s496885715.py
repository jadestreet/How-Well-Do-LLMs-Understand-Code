class Dice():
    def __init__(self,ary):
        self.top = ary[0]
        self.south = ary[1]
        self.east = ary[2]
        self.west = ary[3]
        self.north = ary[4]
        self.bottom = ary[5]

    def get_top(self):
        return self.top

    def rotate_north(self):
        self.top,self.south,self.north,self.bottom = self.south,self.bottom,self.top,self.north
    
    def rotate_south(self):
        self.top,self.south,self.north,self.bottom = self.north,self.top,self.bottom,self.south

    def rotate_west(self):
        self.top,self.west,self.bottom,self.east = self.east,self.top,self.west,self.bottom

    def rotate_east(self):
        self.top,self.west,self.bottom,self.east = self.west,self.bottom,self.east,self.top

    def rotate_horizon(self):
        self.south,self.east,self.north,self.west = self.west,self.south,self.east,self.north

    def get_east(self):
        return self.east
        
dice = Dice(list(map(int,input().split())))
q = int(input())

for i in range(q):
    rot = list(map(int,input().split()))
    if rot[0]==dice.top:
        for _ in range(4):
           dice.rotate_horizon()
           if dice.south==rot[1]:
               h=dice.get_east()
    elif rot[0]==dice.west:
        dice.rotate_east()
        for _ in range(4):
           dice.rotate_horizon()
           if dice.south==rot[1]:
               h=dice.get_east()
    elif rot[0]==dice.bottom:
        dice.rotate_east()
        dice.rotate_east()
        for _ in range(4):
           dice.rotate_horizon()
           if dice.south==rot[1]:
               h=dice.get_east()
    elif rot[0]==dice.east:
        dice.rotate_west()
        for _ in range(4):
           dice.rotate_horizon()
           if dice.south==rot[1]:
               h=dice.get_east()
    elif rot[0]==dice.north:
        dice.rotate_south()
        for _ in range(4):
           dice.rotate_horizon()
           if dice.south==rot[1]:
               h=dice.get_east()
    else:
        dice.rotate_north()
        for _ in range(4):
           dice.rotate_horizon()
           if dice.south==rot[1]:
               h=dice.get_east()
    print(h)