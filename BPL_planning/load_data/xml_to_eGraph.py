import xmltodict
import numpy
import math

from calculations import ctf
from graphs import EnergyGraph
from graphs import EnergyEdge
from graphs import Node

def xml_to_eGraph(netFile, impedance):
    #print("--------->       Load Net from .xml")
    with open(netFile) as netfile:
        tempdata = xmltodict.parse(netfile.read())

    eGraph = EnergyGraph.EnergyGraph()
    for node in tempdata["root"]["bus"]:
        if node == "@type":
            continue

        #print("coordinate", tempdata["root"]["GeneratedCoordinates"][node])
        #print("coordinate X", tempdata["root"]["GeneratedCoordinates"][node]["x"])
        #print("coordinate Y", tempdata["root"]["GeneratedCoordinates"][node]["y"])
        #print("Node", node.partition("n")[2])
        X = float(tempdata["root"]["GeneratedCoordinates"][str(node)]["x"])
        Y = float(tempdata["root"]["GeneratedCoordinates"][str(node)]["y"])

        newNode = Node.Node(eGraph.getUniqueId(), posX=X, posY=Y, zShunt=1, name=node.partition("n")[2])

        eGraph._addNode(newNode)

    nodes = eGraph._getNodes()

    line_dict_list = []
    if tempdata["root"]["line"] != None:
        for line in tempdata["root"]["line"]:
            if line == "@type":
                continue


            fromNodeStr = tempdata["root"]["line"][line]["from_bus"]
            toNodeStr =  tempdata["root"]["line"][line]["to_bus"]

            line_dict = {
                "from_bus": {},
                "to_bus": {},
                "line_type": {}
            }

            line_dict["from_bus"] = fromNodeStr
            line_dict["to_bus"] = toNodeStr
            line_dict["line_type"] = 0

            line_dict_list.append(line_dict)

        '''
        for node in nodes:
            if node.name == fromNodeStr:
                fromNode = node
            elif node.name == toNodeStr:
                toNode = node
            else:
                continue
        
        length = math.sqrt((fromNode.posX-toNode.posX)**2 + (fromNode.posY-toNode.posY)**2)

        newEdge = EnergyEdge.EnergyEdge(eGraph.getUniqueId(), fromNode, toNode, zWave = ctf.calculateGamma()[0], gamma=ctf.calculateGamma()[1], length=length)
        eGraph._addEdge(newEdge)
        '''
    #print(line_dict_list)
    return eGraph, line_dict_list