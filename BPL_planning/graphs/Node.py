from heapq import heappush
from turtle import distance
from typing import Counter
import uuid
import heapq
import calculations.ctf as ctf
# import calculations.dataRates as dataRates
import math
import statistics as stat


class Node():
    __id: uuid.UUID  # unique id
    __posX: int
    __posY: int
    __name: str
    __zShunt: complex  # shunt impedance
    __kvs: float
    __snr: float  # only relevant for routable nodes
    __busTypes: list
    __energyEdgesOut: list  # list of all outgoing EnergyEdges
    __energyEdgesIn: list  # list of all incoming EnergyEdges
    __routingEdgesOut: list  # list of all outgoing RoutingEdges
    __routingEdgesIn: list  # list of all incoming RoutingEdges
    __routableBusTypes: list = ["Rx", "Tx", "Repeater"]  # static list of routable busTypes
    outdated: bool = True  # because of the recursive calculation it's important to know if the cumulated impedance is allready calculated
    isSending: bool = True  # determines if node is sending or not for latency calculation

    @property
    def id(self) -> uuid.UUID:
        return self.__id

    @property
    def posX(self) -> int:
        return self.__posX

    @property
    def posY(self) -> int:
        return self.__posY

    @property
    def name(self) -> str:
        return self.__name

    @property
    def zShunt(self) -> complex:
        return self.__zShunt

    @property
    def kvs(self) -> list:
        return self.__kvs

    @property
    def snr(self) -> float:
        return self.__snr

    @property
    def busTypes(self) -> list:
        return self.__busTypes.copy()

    @property
    def energyEdgesOut(self) -> list:
        return self.__energyEdgesOut.copy()

    @property
    def energyEdgesIn(self) -> list:
        return self.__energyEdgesIn.copy()

    @property
    def routingEdgesOut(self) -> list:
        return self.__routingEdgesOut.copy()

    @property
    def routingEdgesIn(self) -> list:
        return self.__routingEdgesIn.copy()

    def __init__(self, id: uuid.UUID, posX: int = 0, posY: int = 0, zShunt: complex = 0, name: str = "",
                 kvs: list = None):
        self.__id = id
        self.__posX = posX
        self.__posY = posY
        self.__zShunt = 1
        self.__kvs = kvs
        self.__name = name
        self.__busTypes = []
        self.__energyEdgesOut = []
        self.__energyEdgesIn = []
        self.__routingEdgesOut = []
        self.__routingEdgesIn = []

    def copy(self) -> 'Node':
        return Node(id=self.id, posX=self.posX, posY=self.posY, zShunt=self.zShunt)

    def addBusType(self, busType: str):
        if busType not in self.__busTypes:
            self.__busTypes.append(busType)

    def setzShunt(self, zShunt: int):
        self.__zShunt = zShunt

    def removeBusType(self, busType: str):
        if busType == "all":
            self.__busTypes = []
        else:
            self.__busTypes.remove(busType)

    def addEnergyEdgeOut(self, edge):
        if edge not in self.__energyEdgesOut:
            self.__energyEdgesOut.append(edge)

    def removeEnergyEdgeOut(self, edge):
        self.__energyEdgesOut.remove(edge)

    def addEnergyEdgeIn(self, edge):
        if edge not in self.__energyEdgesIn:
            self.__energyEdgesIn.append(edge)

    def removeEnergyEdgeIn(self, edge):
        self.__energyEdgesIn.remove(edge)

    def addRoutingEdgeOut(self, edge):
        if edge not in self.__routingEdgesOut:
            self.__routingEdgesOut.append(edge)

    def removeRoutingEdgeOut(self, edge):
        self.__routingEdgesOut.remove(edge)

    def addRoutingEdgeIn(self, edge):
        if edge not in self.__routingEdgesIn:
            self.__routingEdgesIn.append(edge)

    def removeRoutingEdgeIn(self, edge):
        self.__routingEdgesIn.remove(edge)

    def getZCumu(self) -> complex:
        if self.outdated:
            self.__zCumu = ctf.calculateZCumu(self, self.energyNeighbours)

        return self.__zCumu

    def getBestDataRate3(self, rGraphs, targetNode,
                         rawDataRateKrit=lambda oldRate, newRate, hopCount: min(oldRate, newRate / hopCount)):

        index = 0  # just for tie breaking when pushing into min-heap
        currMaxDataRate = 0
        visited = []
        distanceDict = dict()
        dijkstraTable = []
        #                              -distance    , index, node, prevNode
        heapq.heappush(dijkstraTable, (float('-inf'), index, self, None))

        while dijkstraTable:
            currEntry = heapq.heappop(dijkstraTable)
            visited.append(currEntry[2].name)
            distanceDict[currEntry[2].name] = [-currEntry[0], currEntry[2]]
            for edgeOut in currEntry[2].routingEdgesOut:
                index += 1

                if edgeOut.endNode.name in visited:
                    continue

                dataRate = rawDataRateKrit(currEntry[0], edgeOut.calcDataRate(rGraphs[currEntry[2].name]))
                if dataRate > currMaxDataRate:
                    if edgeOut.endNode.name == targetNode:
                        currMaxDataRate = dataRate
                else:
                    # print("continue")
                    continue

                # print(currEntry[2].name, edgeOut.endNode.name, dataRate)

                nodes = rGraphs[edgeOut.endNode.name]._getNodes()
                endNode = [node for node in nodes if node.name == edgeOut.endNode.name][0]

                heapq.heappush(dijkstraTable, (-dataRate, index, endNode, currEntry[0]))

        if currMaxDataRate == 0:
            return 0, []

        path = [list(distanceDict.keys())[list(distanceDict.values()).index(currMaxDataRate)][0]]
        while path[len(path) - 1] != self.name:
            path.append(distanceDict[path[len(path) - 1]][1])

        return currMaxDataRate, path

    def getBestDataRate(self, rGraphs, targetNode,
                        rawDataRateKrit=lambda oldRate, newRate, hopCount: min(oldRate, newRate / hopCount)):

        # print("Target:", targetNode)

        counter = 0  # just for tie breaking when pushing into min-heap
        currMaxDataRate = 0
        visited = set()
        distances = dict()
        dijkstraTable = []

        #                              -distance    , counter, node
        heapq.heappush(dijkstraTable, (float('-inf'), counter, self))

        while dijkstraTable:

            currEntry = heapq.heappop(dijkstraTable)
            currDataRate = -currEntry[0]
            currNode = currEntry[2]
            currNodeName = currNode.name

            if currNodeName in visited: continue
            visited.add(currNodeName)

            for edgeOut in currNode.routingEdgesOut:

                counter += 1
                edgeOutName = edgeOut.endNode.name

                if edgeOutName in visited: continue

                dataRate = round(rawDataRateKrit(currDataRate, edgeOut.calcDataRate(rGraphs[currNodeName])), 5)
                # print("Edge:", currNodeName, edgeOutName)
                # print("DataRate:", dataRate, currMaxDataRate)
                if dataRate <= currMaxDataRate: continue

                if edgeOutName == targetNode:
                    currMaxDataRate = dataRate

                if (edgeOutName not in distances) or (dataRate > distances[currNodeName][0]):
                    distances[edgeOutName] = [dataRate, currNodeName]

                    nodes = rGraphs[edgeOutName]._getNodes()
                    endNode = [node for node in nodes if node.name == edgeOutName][0]

                    heapq.heappush(dijkstraTable, (-dataRate, counter, endNode))
                    # print("Pushed")

        if currMaxDataRate == 0:
            return 0, []

        path = [targetNode]
        while path[len(path) - 1] != self.name:
            path.append(distances[path[len(path) - 1]][1])
        path.reverse()

        return currMaxDataRate, path

    def getBestDataRate2(self, rGraphs, targetNode, sourceNodes=[], currHopCount=0, currRawDataRate=0,
                         rawDataRateKrit=lambda oldRate, newRate, hopCount: min(oldRate, newRate / hopCount),
                         currMaxDataRate=0) -> float:
        if (not self.isRoutable()):
            return None
        if (self == targetNode):
            return currRawDataRate, []
            return currRawDataRate / currHopCount, []
        if (len(self.routingEdgesOut) == 0):
            return 0, []
        if (len(sourceNodes) != 0 and (currRawDataRate < 27000 or currRawDataRate < currMaxDataRate)):
            return 0, []

        print(sourceNodes)
        print(currRawDataRate)

        oldRawDataRate = currRawDataRate
        currHopCount += 1
        dataRateDict = dict()
        bestEdgeDict = dict()

        for edgeOut in self.routingEdgesOut:

            if (edgeOut.endNode.name in sourceNodes):
                continue

            if (len(sourceNodes) == 0):
                currRawDataRate = edgeOut.calcDataRate(rGraphs[edgeOut.endNode.name])
            else:
                currRawDataRate = rawDataRateKrit(oldRawDataRate, edgeOut.calcDataRate(rGraphs[edgeOut.endNode.name]),
                                                  currHopCount)
            # print("test: ",currRawDataRate)
            nodes = rGraphs[edgeOut.endNode.name]._getNodes()
            endNode = [node for node in nodes if node.name == edgeOut.endNode.name][0]
            # print(edgeOut.startNode.name, edgeOut.endNode.name)

            newSourceNodes = sourceNodes.copy()
            newSourceNodes.append(self.name)

            if len(dataRateDict.items()) == 0:
                result = endNode.getBestDataRate(rGraphs, targetNode, newSourceNodes, currHopCount, currRawDataRate,
                                                 rawDataRateKrit, 0)
            else:
                result = endNode.getBestDataRate(rGraphs, targetNode, newSourceNodes, currHopCount, currRawDataRate,
                                                 rawDataRateKrit, max(dataRateDict.values()))
            dataRateDict[edgeOut] = result[0]
            bestEdgeDict[edgeOut] = result[1]

        if len(dataRateDict.items()) == 0:
            return 0, []

        # print(dataRateDict, dataRateDict.get)
        bestEdge = max(dataRateDict, key=dataRateDict.get)
        bestEdgeList = bestEdgeDict[bestEdge]
        bestEdgeList.append(bestEdge)

        return dataRateDict[bestEdge], bestEdgeList

    def calc_SNR(self) -> float:
        # TODO: use existing snr calculation
        return

    def isRoutable(self) -> bool:
        return len([type for type in self.busTypes if type in self.__routableBusTypes]) > 0