import sys
import os
import random
import time
from multiprocessing import Process
import numpy

# dirname = os.path.dirname(__file__)
# sys.path.append(os.path.join(dirname, './path/to/file/you/want'))
sys.path.append("./")

from graphs.EnergyGraph import EnergyGraph
from graphs.EnergyEdge import EnergyEdge
from graphs.Node import Node

leaflist = []


def addChildNodes(eGraph: EnergyGraph, rootNode: Node, childCount: int, lvlCount: int) -> Node:
    if lvlCount == 0: return

    newNode: Node
    for _ in range(0, childCount):
        newNode = Node(eGraph.getUniqueId(), zShunt=50 + 89j)
        newEdge = EnergyEdge(eGraph.getUniqueId(), rootNode, newNode, zWave=89, length=15, gamma=0.02)
        addChildNodes(eGraph, newNode, childCount, lvlCount - 1)

        eGraph._addNode(newNode)
        eGraph._addEdge(newEdge)
        if lvlCount == 1:
            leaflist.append(newNode)

    return newNode


eGraph = EnergyGraph()
rootNode = Node(eGraph.getUniqueId(), zShunt=1)

# newNode = Node(eGraph.getUniqueId(), zShunt=2)
# newEdge = EnergyEdge(eGraph.getUniqueId(), rootNode, newNode, zWave=1)

# print("Root < obj, list > : ", hex(id(rootNode)), ", ", hex(id(rootNode.energyEdgesOut)))
# print("Root < obj, list > : ", hex(id(newNode)), ", ", hex(id(newNode.energyEdgesOut)))

# newNode2 = Node(eGraph.getUniqueId())
# newEdge2 = EnergyEdge(eGraph.getUniqueId(), rootNode, newNode2)

newNode = addChildNodes(eGraph, rootNode, 3, 7)
eGraph._addNode(rootNode)

# eGraph._addNode(newNode)
# eGraph._addEdge(newEdge)

print("initialized")

for leaf in leaflist:
    path = eGraph.shortestPath_NodeCount(rootNode, leaf)
    path = eGraph.convertNodePath2EdgePath(path)
    # print(path)
    if leaf == leaflist[0] or leaf == leaflist[len(leaflist) - 1]:
        starttime = time.time()
        ctf = eGraph.calcCTF(path)
        snr = eGraph.calcSNR(ctf)
        print("ctf: ", numpy.abs(ctf))
        print("snr: ", snr)
        print("time: ", time.time() - starttime, "\n")
    else:
        ctf = eGraph.calcCTF(path)
        snr = eGraph.calcSNR(ctf)

# eGraph.plot()
