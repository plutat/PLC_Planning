import uuid
import math
from graphs.Edge import Edge
from graphs.Node import Node
from calculations import ctf


class EnergyEdge(Edge):
    __length: float
    __gamma: float
    __zWave: complex  # wave impedance
    __zSubst: complex  # substituted impedance of the outgoing subgraph
    __ctf: float
    __linetype: str
    __MSLINK: int
    outdated: bool = True  # because of the recursive calculation it's important to know if the ctf value is allready calculated

    @property
    def length(self) -> float:
        return self.__length

    @property
    def gamma(self) -> float:
        return self.__gamma

    @property
    def zWave(self) -> complex:
        return self.__zWave

    @property
    def zTrans(self) -> complex:
        return self.__zTrans

    @property
    def ctf(self) -> float:
        return self.__ctf

    @property
    def linetype(self) -> str:
        return self.__linetype

    @property
    def MSLINK(self) -> int:
        return self.__MSLINK

    def __init__(self, id: uuid.UUID, startNode: Node, endNode: Node, zWave: complex = 0, gamma: float = 0,
                 length: float = 0, type: str = "", MSLINK: int = 0):
        super().__init__(id, startNode, endNode)
        self.__zWave = zWave
        self.__gamma = gamma
        self.__length = length
        self.__linetype = type
        self.__MSLINK = MSLINK
        startNode.addEnergyEdgeOut(self)
        endNode.addEnergyEdgeIn(self)

    def getZSubst(self) -> complex:
        if self.outdated:
            self.__zSubst = ctf.calculateZSubst(self.endNode, zWave=self.zWave, gamma=self.gamma, length=self.length)
            self.outdated = False

        return self.__zSubst