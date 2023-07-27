from graphs.EnergyGraph import EnergyGraph
from graphs.Graph_NetworkX import Graph_NetworkX
from graphs.Node import Node
from graphs.RoutingEdge import RoutingEdge
from calculations import noise_source, snr
import math
import statistics as stat
import numpy as np

class RoutingGraph(Graph_NetworkX):
    __energyGraph: EnergyGraph
    __noisefloor: float
    __txpsd: float
    __ctf: dict

    @property
    def noisefloor(self) -> float:
        return self.__noisefloor

    @property
    def txpsd(self) -> float:
        return self.__txpsd

    @property
    def ctf(self) -> float:
        return self.__ctf

    # def __init__(self, energyGraph: EnergyGraph, noisefloor: float, txpsd: float):
    def __init__(self, energyGraph: EnergyGraph, noisefloor, txpsd):
        super().__init__()
        self.__energyGraph = energyGraph
        self.__noisefloor = noisefloor
        self.__txpsd = txpsd
        self.__ctf = energyGraph.ctf

        # print("Init RoutingGraph")

        for node in energyGraph._getNodes():
            self._addNode(node)

        # print("Nodes Added")

        self.updateRoutingGraph()

    # TODO: def calcLocalNoise():

    # deletes wrong RoutingEdges/Nodes and adds missing RoutingEdges/Nodes
    def updateRoutingGraph(self):

        newRoutableNodes = []
        newNotRoutableNodes = []
        for node in self._getNodes():
            if node.isRoutable() and (len(node.routingEdgesOut) + len(node.routingEdgesIn)) == 0:
                # the node is recently routable
                newRoutableNodes.append(node)
            elif not node.isRoutable() and (len(node.routingEdgesOut) + len(node.routingEdgesIn)) != 0:
                # the node is no longer routable
                newNotRoutableNodes.append(node)

        # print("Nodes categorized")

        for node in newRoutableNodes:
            # print(node.name)
            # print("get RoutingNeighboursIn")
            neighboursIn = [edge.startNode for edge in node.energyEdgesIn]
            changed = True
            while changed:
                # print([node.name for node in neighboursIn])
                changed = False
                neighboursInNew = []
                for neighbour in neighboursIn:
                    if not neighbour.isRoutable():
                        # print(neighbour.name, "is not routable, bustypes: ", neighbour.busTypes)
                        neighboursInNew.extend([edge.startNode for edge in neighbour.energyEdgesIn if
                                                edge.startNode not in neighboursInNew])
                        changed = True
                    else:
                        neighboursInNew.append(neighbour)
                neighboursIn = neighboursInNew.copy()

            # print("get RoutingNeighboursOut")
            neighboursOut = [edge.endNode for edge in node.energyEdgesOut]
            changed = True
            while changed:
                # print([node.name for node in neighboursOut])
                changed = False
                neighboursOutNew = []
                for neighbour in neighboursOut:
                    if not neighbour.isRoutable():
                        # print(neighbour.name, "is not routable, bustypes: ", neighbour.busTypes)
                        neighboursOutNew.extend(
                            [edge.endNode for edge in neighbour.energyEdgesOut if edge.endNode not in neighboursOutNew])
                        changed = True
                    else:
                        neighboursOutNew.append(neighbour)
                neighboursOut = neighboursOutNew.copy()

            # print("remove edges between in and out neighbours")
            for neighbourIn in neighboursIn:
                for edge in neighbourIn.routingEdgesIn:
                    if edge.endNode in neighboursOut:
                        self._removeEdges([edge])
                        edge.startNode.removeRoutingEdgeOut(edge)
                        edge.endNode.removeRoutingEdgeIn(edge)

            # print("add edges between node and in and out neighbours")
            for neighbourIn in neighboursIn:
                if not self._hasEdge((neighbourIn, node)):
                    newEdge = RoutingEdge(self.getUniqueId(), neighbourIn, node, self.convertNodePath2EdgePath(
                        self.__energyGraph.shortestPath_NodeCount(neighbourIn, node)))
                    self._addEdge(newEdge)
            for neighbourOut in neighboursOut:
                if not self._hasEdge((node, neighbourOut)):
                    newEdge = RoutingEdge(self.getUniqueId(), node, neighbourOut, self.convertNodePath2EdgePath(
                        self.__energyGraph.shortestPath_NodeCount(node, neighbourOut)))
                    self._addEdge(newEdge)

        for node in newNotRoutableNodes:
            # the node is no longer routable

            self._removeEdges(node.routingEdgesOut)
            self._removeEdges(node.routingEdgesIn)
            for edgeIn in node.routingEdgesIn:
                for edgeOut in node.routingEdgesOut:
                    newEdge = RoutingEdge(self.getUniqued(), edgeIn.startNode, edgeOut.endNode,
                                          self.convertNodePath2EdgePath(
                                              self.__energyGraph.shortestPath_NodeCount(edgeIn.startNode,
                                                                                        edgeOut.endNode)))
                    self._addEdge(newEdge)
                    node.removeRoutingEdgeIn(edgeOut)
                node.removeRoutingEdgeIn(edgeIn)

        return

    def calcSNR_ofPath(self, path, local_noise=0):
        ctfList = self.__energyGraph.calcCTF(path)
        return snr.calculateSNR(ctfList, self.noisefloor + local_noise, self.txpsd)

    ### old approach using precalculated ctf values, deprecated causes to much computation
    def calcSNR(self, start_node, end_node, new_noise=0) -> list:
        ctfList = self.ctf[(start_node.name, end_node.name)]
        return snr.calculateSNR(ctfList, self.noisefloor + new_noise, self.txpsd)

    #### Returns the SNR Matrix , also deprecated for too much runtime
    def calcSNRMatrix(self):
        matrix = {}
        agent_list = self.__energyGraph.get_Agents()
        for start_node in agent_list:
            for end_node in agent_list:
                if start_node != end_node:
                    new_noise_add = 0
                    ###new_noise_add = noise_source.set_noise_sources(self, end_node, agent_list)
                    snr_array = self.calcSNR(start_node, end_node, new_noise=new_noise_add)
                    snr_in_mW = stat.mean(snr_array)
                    snr = (10 * (math.log10(snr_in_mW / 1000))) + 30
                    matrix[(start_node.name, end_node.name)] = snr
                    matrix[(end_node.name, start_node.name)] = snr
        return matrix

    def tdmaAsynch_sp_multi_tx(self):
        # calculates asynchronous TDMA data rate of single rx-tx-paths, including hops
        # returns list of tx with respective lists of all rx-rates
        rx_list: list
        tx_list: list

        rx_list = self.get_RX()
        # tx_list = self.get_TX()
        tx_list = []
        tx_list.append(self.get_TX())

        tdma_rates = {}
        # tdma_to_tx_list = {}
        datarate_list = []

        for tx in tx_list:

            for rx in rx_list:
                route_list = self.shortestPath_NodeCount(tx, rx)
                route_list = self.convertNodePath2EdgePath_routing(route_list)
                link_dr_list = []

                for edge in route_list:
                    edge.calcDataRate(self)
                    link_dr_list.append(edge.physDataRate)

                dr_list_arr = np.array(link_dr_list)
                dr_rev_arr = 1 / dr_list_arr
                tdma_rates[(tx.name, rx.name)] = (1 / sum(dr_rev_arr))
                datarate_list.append(1 / sum(dr_rev_arr))

            # tdma_to_tx_list.append(tdma_rates)

        return tdma_rates, datarate_list

    #### returns list of nodes where repeaters can be placed
    def get_Potential(self) -> list:
        return self.__energyGraph.get_Potential()

    ## placing repeaters on the network, gets list of 0 and 1, len of input =len of pot_repeater,

    #### Get list of all nodes that are repeaters
    def get_Repeater(self) -> list:
        return self.__energyGraph.get_Repeater()

    ## Get TX node
    def get_RX(self):
        return self.__energyGraph.get_RX()

    def get_TX(self):
        return self.__energyGraph.get_TX()

    #### Get list of all nodes that are either RX or TX ,or repeaters
    def get_Agents(self) -> list:
        return self.__energyGraph.get_Agents()

    def place_repeater(self, placement) -> list:
        # places repeaters according to individuum
        return self.__energyGraph.place_repeater(placement)

    def place_repeater_alt(self, place) -> list:
        # places repeater at given node name
        return self.__energyGraph.place_repeater_alt(place)

    # returns shortest Path based on the node count
    def shortestPath_NodeCount(self, startnode: Node, endnode: Node):
        return super()._shortestPath(startnode, endnode)

    # returns shortest Path based on the snr values
    def shortestPath_SNR(self, startnode: Node, endnode: Node):
        # TODO: to be implemented
        return
