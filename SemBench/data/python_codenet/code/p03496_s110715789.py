n = int(input())
as_ = list(int(i) for i in input().split())


def output_history(history):
    print(len(history))
    for h in history:
        print('{0} {1}'.format(h[0], h[1]))


def distribute(list_, hstr, x, y):
    list_[y] += list_[x]
    hstr.append((x + 1, y + 1))  # Fortran式
    return list_, hstr


history = []

# 正負どちらかに寄せる
# MaxMin大きく外れている方に寄せる
if abs(max(as_)) > abs(min(as_)):
    # 正に寄せる
    # 正のMaxを負の要素に繰り返し分配
    x = as_.index(max(as_))
    while not all([a >= 0 for a in as_]):
        for y, a in enumerate(as_):
            if a < 0:
                as_, history = distribute(as_, history, x, y)

    # 前から順に走査し反転箇所で前の要素を後ろの要素に足し合わせる
    for x in range(len(as_) - 1):
        # 反転箇所で
        if as_[x + 1] - as_[x] < 0:
            as_, history = distribute(as_, history, x, x + 1)

else:
    # 負に寄せる
    # 負のMaxを正の要素に繰り返し分配
    x = as_.index(min(as_))
    while not all([a <= 0 for a in as_]):
        for y, a in enumerate(as_):
            if a > 0:
                as_, history = distribute(as_, history, x, y)

    # 後ろから順に走査し反転箇所で後ろの要素を前の要素に足し合わせる
    for x in reversed(range(len(as_) - 1)):
        # 反転箇所で
        if as_[x + 1] - as_[x] < 0:
            as_, history = distribute(as_, history, x + 1, x)

output_history(history)
