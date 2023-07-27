from abc import ABC, abstractmethod
import uuid
from graphs.Node import Node

class Edge(ABC):
    __id: uuid.UUID
    __startNode: Node
    __endNode: Node

    @property
    def id(self) -> uuid.UUID:
        return self.__id

    @property
    def startNode(self) -> Node:
        return self.__startNode

    @property
    def endNode(self) -> Node:
        return self.__endNode

    def __init__(self, id: uuid.UUID, startNode: Node, endNode: Node):
        self.__id = id
        self.__startNode = startNode
        self.__endNode = endNode

    def copy(self) -> 'Edge':
        return Edge(id=self.__id, startNode=self.__startNode, endNode=self.__endNode)