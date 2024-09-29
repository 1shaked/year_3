# Description: Search in 2-3 tree
def member(t, x):
    if t is None:
        return False
    if t.is_leaf():
        return x in t.keys
    if x < t.keys[0]:
        return member(t.children[0], x)
    if len(t.keys) == 3 and x >= t.keys[1]:
        return member(t.children[2], x)
    if len(t.keys) == 3 and x >= t.keys[0]:
        return member(t.children[1], x)
    return member(t.children[1], x)
