import uuid
from graphs.Edge import Edge
from graphs.Node import Node
from calculations import dataRates


class RoutingEdge(Edge):

    @property
    def currDataRateLoad(self):
        return self.__currDataRateLoad

    @property
    def physDataRate(self):
        return self.__physDataRate

    @property
    def energyEdges(self):
        return self.__energyEdges

    def __init__(self, id: uuid.UUID, startNode: Node, endNode: Node, energyEdges: list()):
        super().__init__(id, startNode, endNode)
        self.__energyEdges = energyEdges
        self.__physDataRate = None
        self.__currDataRateLoad = 0
        startNode.addRoutingEdgeOut(self)
        endNode.addRoutingEdgeIn(self)

    def calcDataRate(self, rGraph) -> float:
        if self.__physDataRate is None:
            snr = rGraph.calcSNR_ofPath(self.__energyEdges)
            self.__physDataRate = dataRates.ofdmDataRate(snr)

        # print("PhyDataRate:", "(", self.startNode.name, self.endNode.name, ")", self.__physDataRate)
        return max(0, self.__physDataRate - self.__currDataRateLoad)

    def addDataRateLoad(self, load):
        self.__currDataRateLoad += load

    def calcSNRRate(self, rGraph) -> float:
        return (rGraph.calcSNR_ofPath(self.__energyEdges))

    def setphysDataRate(self, physDatarate):
        self.__physDataRate = physDatarate