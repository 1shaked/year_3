def unionInner(big, small):
    
    for item in small:
        item.head = big.head
        big.tail = item.tail
    big.size += small.size
    return big

def unionSet(s1, s2):
    if s1.size > s2.size:
        return unionInner(s1, s2)
    else:
        return unionInner(s2, s1)