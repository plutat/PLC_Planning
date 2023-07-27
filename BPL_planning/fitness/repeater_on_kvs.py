#puts repeater on every node with MSLINK_KVS connection
def set_repeater (eGraph):
    nodes = eGraph._getNodes()

    for node in nodes:
        if node.kvs != None and "Tx" not in node.busTypes:
            node.addBusType("Repeater")
        #print(node.name, ": ", node.busTypes)