def passMessageToNetwork(G, T , r , I):
    # This function will pass the message to all the nodes in I 
    node = r
    for i in I:
        if i.p != node:
            # send this to message to all node children
            for child in node.children:
                passMessageToNetwork(G, T, child, i)
            continue
        node.saveValue(i.v)
