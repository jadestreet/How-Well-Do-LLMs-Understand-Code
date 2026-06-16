# 1.py — Semantics-rich small program

def helper(x):
    if x > 0:
        return inner(x - 1)
    return 0

def inner(y):
    if y == 0:
        return leaf()
    return y

def leaf():
    return 42

def unrelated(z):
    return z * z

def has_loops(n, m):
    total = 0
    for i in range(n):               # loop header A: "for i in range(n):"
        total += i                   # loop body A
    while m > 0:                     # loop header B: "while m > 0:"
        m -= 1                       # loop body B statement "m -= 1"
    return total + m

def data_flow(a, b):
    temp = a + 1                     # def_snippet_1: "temp = a + 1"
    b = b * 2                        # def_snippet_2: "b = b * 2"
    c = temp + b                     # uses temp and b
    temp = 0                         # redefinition of temp (no later use)
    d = 5                            # def_snippet_3: "d = 5" (never used)
    return c

def liveness_func(flag):
    x = 0
    if flag:
        x = 3
    y = x + 1
    return y

def liveness2():
    p = 10
    q = 20
    p = 30
    return q

def dead_code_demo():
    return 1
    print("never")  # unreachable

def dead_code_demo_2():
    if False:
        x = 1  # unreachable
    return 0
