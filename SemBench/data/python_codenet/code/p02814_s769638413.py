import fractions
from functools import reduce
def lcm_base(x, y):
    return (x * y) // fractions.gcd(x, y)
def lcm_list(numbers):
    return reduce(lcm_base, numbers, 1)
nm=list(map(int, input().split()))
a=list(map(int, input().split()))
n=nm[0]
m=nm[1]
b=0
c=a[0]
dnum=0
while c%2==0:
    dnum+=1
    c=c//2
for i in range(len(a)):
    c=a[i]
    dnum1=0
    while c%2==0:
        dnum1+=1
        c=c//2
    #print(dnum)
    if dnum1!=dnum:
        b=1
        break

#print(a)
if b==1:
    print(0)
else:
    for i in range(len(a)):
        a[i]=a[i]//2
    #print(a)
    amc=lcm_list(a)
    #print(amc)
    # version3.5にてgcdがfractionsからmathに移動した
    print(int((m+amc)/(2*amc)))

