MAX = 3
MIN = 2
def search():
    pass`

def merge():
    pass

def split():
    pass
# inserting in a 2-3 tree

def insert(t, v):
    loc = search(t, v)
    loc.push(v)
    if loc.children.len > MAX:
        # merge either the left or right child
        if loc.left.children.len < MAX:
            merge(loc, loc.left) 

        elif loc.right.children.len < MAX:
            merge(loc, loc.right)

        else:
            # split the node
            split(loc)
            insert(t, v)