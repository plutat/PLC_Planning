from abc import ABC, abstractmethod
import uuid
from graphs.Node import Node
from graphs.Edge import Edge


class Graph(ABC):

    @abstractmethod
    def _shortestPath(self, startnode: Node, endnode: Node):
        pass

    def convertNodePath2EdgePath(self, path: list) -> list:
        edgePath: list = []
        for i in range(0, len(path) - 1):
            edge = next(filter(lambda edge: edge.endNode == path[i + 1], path[i].energyEdgesOut))
            edgePath.append(edge)
        return edgePath

    def convertNodePath2EdgePath_routing(self, path: list) -> list:
        edgePath: list = []
        for i in range(0, len(path) - 1):
            edge = next(filter(lambda edge: edge.endNode == path[i + 1], path[i].routingEdgesOut))
            edgePath.append(edge)
        return edgePath

    @abstractmethod
    def _addNode(self, node: Node):
        pass

    @abstractmethod
    def _addEdge(self, edge: Edge):
        pass

    # @abstractmethod
    # def _deleteNode(self):
    #     pass

    @abstractmethod
    def _getEdges(self):
        pass

    @abstractmethod
    def _getNodes(self):
        pass

    @abstractmethod
    def getUniqueId(self) -> uuid.UUID:
        pass

    @abstractmethod
    def getNeighbourNodes(self, node: Node, range: int):
        pass

    # @abstractmethod
    # def getIncomingEdges(self, node: Node):
    #     pass

    # @abstractmethod
    # def getOutgoingEdges(self, node: Node):
    #     pass

    # @abstractmethod
    # def removeEdges(self, edges: list):
    #     pass

    @abstractmethod
    def plot(self):
        pass