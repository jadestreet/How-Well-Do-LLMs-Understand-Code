def after_return():
    keep = 1
    return keep
    never_after_return = 2


def false_branch():
    before = 0
    if False:
        never_in_false = 3
    after = before + 1
    return after
