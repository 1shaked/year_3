
import random


class Node:
    pass
# handle insert operation in a skip list, where we have len of the distance between the nodes in level 0
def insert(t, v):
    prevEl , nextEl = search(t, v)
    prevParentPath = searchPath(t, prevEl) 
    prevEl.next = Node(v, prevEl.next)
    v.next = nextEl
    for path in prevParentPath:
        if path.dir != 'UP':
            continue
        if path.v <= v and path.next.v >= v:
            path.size += 1
        


def insert(t, v, level):
    prevEl , nextEl = search(t, v)
    prevParentPath, distanceFromV = searchPath(t, prevEl) 
    distanceToNext = prevParentPath.size
    remainingDistance = distanceToNext - distanceFromV
    prevEl.next = Node(v, prevEl.next)
    v.next = nextEl
    for path in prevParentPath:
        if path.dir != 'UP':
            continue
        if path.v <= v and path.next.v >= v:
            path.size += 1
    ADD_TO_TOP = random.choice([True, False])
    if ADD_TO_TOP:
        insert(t.levels[level + 1])
        
    return t
        



def search(t, v):
    pass

def searchPath(t, v):
    pass

def split(t):
    pass

def delete(t, v):
    prevEl , nextEl, didFound = search(t, v)
    prevParentPath, distanceFromV = searchPath(t, prevEl) 
    if not didFound:
        prevEl.size - 1
    else: 
        prevEl.size += v.size - 1

    prevEl.next = nextEl
    delete(t.levels[1] , v  )



def findOrderStatistic(t, k, init):
    start = init
    end = init.next
    if start.size == k:
        return start
    if start.size > k and end.size < k:
        return findOrderStatistic(t, k , start)
    if start.size < k:
        return findOrderStatistic(t, k - start.size, end)
    
    