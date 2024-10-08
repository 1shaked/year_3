
class Node:
    pass
# handle insert operation in a skip list, where we have len of the distance between the nodes in level 0
def insert(t, v):
    prevEl , nextEl = search(t, v)
    prevParentPath = searchPath(t, prevEl) 
    # tempPath = prevParentPath
    for path in prevParentPath:
        if path.dir != 'UP':
            continue
        if path.v <= v and path.next.v >= v:
            path.size += 1
        


def search(t, v):
    pass

def searchPath(t, v):
    pass

def split(t):
    pass