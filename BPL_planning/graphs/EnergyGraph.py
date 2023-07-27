from time import sleep
from graphs.Node import Node
from graphs.Graph_NetworkX import Graph_NetworkX
from graphs.EnergyEdge import EnergyEdge
import calculations.ctf as ctf
from load_data import load_netconfig
from load_data import json_to_eGraph
from load_data import xml_to_eGraph
#from fitness import repeater_on_kvs
from calculations import ctf
import math
import calculations.snr as snr
import networkx

cond = True


class EnergyGraph(Graph_NetworkX if cond else object):

    @property
    def noisefloor(self) -> float:
        return self.__noisefloor

    def __init__(self):
        super().__init__()
        self.ctf = {}

    # updates the ctf values of some selected edges
    def updateCTFsSelected(self, edgeList: list):
        for edge in edgeList:
            edge.outdated = True
        for edge in edgeList:
            if edge.outdated:
                edge.calcCTF()
        return

    # calculates the ctf of a given path
    def calcCTF(self, path: list) -> complex:
        return ctf.calculateCTF(path)

    def updateCTF(self):
        node = self.get_TX()
        for endnode in self.get_RX():
            ### We calculate all the CTF once at the start so we dont need to recalculate them in every iteration of the optimization allgorithmes

            if node != endnode:
                ctf_path = self.shortestPath_NodeCount(node, endnode)
                ctf_path = self.convertNodePath2EdgePath(ctf_path)
                ctf_temp = self.calcCTF(ctf_path)

                self.ctf[(node, endnode)] = ctf_temp
                self.ctf[(endnode, node)] = ctf_temp
        return

        # returns shortest Path based on the node count

    def shortestPath_NodeCount(self, startnode: Node, endnode: Node):
        return self._shortestPath(startnode, endnode)

    # returns shortest Path based on the ctf values
    def shortestPath_CTF(self, startnode: Node, endnode: Node):
        # TODO: to be implemented
        return

    # returns a dict
    # key: node
    # val: [neighbours, linetype] (not directed)
    def line_dict_list2ref_dict(self, line_dict_list):
        map = dict()
        nodes = self._getNodes()
        for node in nodes:
            map[node.name] = node

        ref_dict = dict()
        for line in line_dict_list:
            if map[line["from_bus"]] not in ref_dict:
                ref_dict[map[line["from_bus"]]] = list()
            if map[line["to_bus"]] not in ref_dict:
                ref_dict[map[line["to_bus"]]] = list()

            if "length" not in line:
                line["length"] = None

            ref_dict[map[line["from_bus"]]].append([map[line["to_bus"]], line["line_type"], line["length"]])
            ref_dict[map[line["to_bus"]]].append([map[line["from_bus"]], line["line_type"], line["length"]])

        return ref_dict

    def add_edges(self, line_dict_list):

        ref_dict = self.line_dict_list2ref_dict(line_dict_list)
        nodes = self._getNodes()

        for node in nodes:  # find TX
            if "Tx" in node.busTypes:
                TX = node
                break

        nodes2check = [TX]
        nodesChecked = []
        while len(nodes2check) > 0:
            edges = ref_dict[nodes2check[0]]
            for edge in edges:
                # print(nodes2check[0].name, edge[0].name)
                if edge[0] in nodesChecked:
                    # print("Stelle 1")
                    continue
                # ! one edge in Gemeinde2 has no length
                if edge[2] is None:
                    edge[2] = ((nodes2check[0].posX - edge[0].posX) ** 2 + (
                                nodes2check[0].posY - edge[0].posY) ** 2) ** 0.5
                newEdge = EnergyEdge(self.getUniqueId(), nodes2check[0], edge[0], ctf.calculateGamma()[0],
                                     ctf.calculateGamma()[1], edge[2], edge[1])
                self._addEdge(newEdge)
                if edge[0] not in nodesChecked and edge[0] not in nodes2check:
                    nodes2check.append(edge[0])
            nodesChecked.append(nodes2check.pop(0))

        return 1

    # adds edges from line_dict_list into eGraph
    def add_edges2(self, line_dict_list):
        nodes = self._getNodes()
        new_neighbours = []
        delete_lines = []

        for node in nodes:  # find TX
            # print(node.name)
            if "Tx" in node.busTypes:
                # print("TX: ", node.name)
                TX = node
                break

        for line in line_dict_list:  # adds all lines starting from TX
            if line["from_bus"] == TX.name:
                for node in nodes:
                    if node.name == line["to_bus"]:
                        to_bus = node
                newEdge = EnergyEdge(self.getUniqueId(), TX, to_bus, ctf.calculateGamma()[0], ctf.calculateGamma()[1],
                                     math.sqrt((TX.posX - to_bus.posX) ** 2 + (TX.posY - to_bus.posY) ** 2),
                                     line["line_type"])
                self._addEdge(newEdge)
                new_neighbours.append(to_bus)
                delete_lines.append(line)
            if line["to_bus"] == TX.name:  # adds all lines ending in TX, but with TX as startingpoint
                for node in nodes:
                    if node.name == line["from_bus"]:
                        from_bus = node
                newEdge = EnergyEdge(self.getUniqueId(), TX, from_bus, ctf.calculateGamma()[0], ctf.calculateGamma()[1],
                                     math.sqrt((TX.posX - from_bus.posX) ** 2 + (TX.posY - from_bus.posY) ** 2),
                                     line["line_type"])
                new_neighbours.append(from_bus)
                self._addEdge(newEdge)
                delete_lines.append(line)

        line_dict_list = [line for line in line_dict_list if
                          line not in delete_lines]  # deletes added lines from line_dict_list
        self.add_edges_to_neighbours(new_neighbours, line_dict_list)
        return 1

    # adds edges from every node in old_neighbours into eGraph
    def add_edges_to_neighbours(self, old_neighbours, line_dict_list):
        nodes = self._getNodes()
        while len(line_dict_list) > 0:
            new_neighbours = []
            delete_lines = []
            for neighbour in old_neighbours:
                for line in line_dict_list:
                    if line["from_bus"] == neighbour.name:  # adds all lines starting from node
                        for node in nodes:
                            if node.name == line["to_bus"]:
                                to_bus = node
                        newEdge = EnergyEdge(self.getUniqueId(), neighbour, to_bus, ctf.calculateGamma()[0],
                                             ctf.calculateGamma()[1], math.sqrt(
                                (neighbour.posX - to_bus.posX) ** 2 + (neighbour.posY - to_bus.posY) ** 2),
                                             line["line_type"])
                        self._addEdge(newEdge)
                        new_neighbours.append(to_bus)
                        delete_lines.append(line)
                        # continue
                    if line[
                        "to_bus"] == neighbour.name:  # adds all lines ending in node, but with node as startingpoint
                        for node in nodes:
                            if node.name == line["from_bus"]:
                                from_bus = node
                        newEdge = EnergyEdge(self.getUniqueId(), neighbour, from_bus, ctf.calculateGamma()[0],
                                             ctf.calculateGamma()[1], math.sqrt(
                                (neighbour.posX - from_bus.posX) ** 2 + (neighbour.posY - from_bus.posY) ** 2),
                                             line["line_type"])
                        new_neighbours.append(from_bus)
                        self._addEdge(newEdge)
                        delete_lines.append(line)
                        # continue

            old_neighbours = new_neighbours.copy()
            line_dict_list = [line for line in line_dict_list if
                              line not in delete_lines]  # deletes added lines from line_dict_list

        return 1

    #### returns list of nodes where repeaters can be placed
    def get_Potential(self) -> list:
        pot_repaters = []
        for node in self._getNodes():
            if "Tx" not in node.busTypes and "Rx" not in node.busTypes and node.kvs == None and (
                    node.energyEdgesIn != [] or node.energyEdgesOut != []):
                pot_repaters.append(node)
        return pot_repaters

    ## placing repeaters on the network, gets list of 0 and 1, len of input =len of pot_repeater,
    def place_repeater(self, placement):
        pot_repaters = self.get_Potential()
        for x in range(len(placement)):
            if placement[x]:
                pot_repaters[x].addBusType("Repeater")
            else:
                pot_repaters[x].removeBusType("all")
        return

    def place_repeater_alt(self, placement):
        pot_repaters = self.get_Potential()
        for x in pot_repaters:
            if placement[x.name]:
                x.addBusType("Repeater")
            else:
                x.removeBusType("all")
        return
        #### Get list of all nodes that are repeaters

    def get_Repeater(self) -> list:
        repaters = []
        for node in self._getNodes():
            if "Repeater" in node.busTypes:
                repaters.append(node)
        return repaters

    ## Get TX node
    def get_RX(self):
        rx_list = []
        for node in self._getNodes():
            if "Rx" in node.busTypes:
                rx_list.append(node)
        return rx_list

    def get_TX(self):
        for node in self._getNodes():
            if "Tx" in node.busTypes:
                return node

        return "n0"

    #### Get list of all nodes that are either RX or TX ,or repeaters
    def get_Agents(self) -> list:
        relevant = []
        for node in self._getNodes():
            if "Rx" in node.busTypes or "Tx" in node.busTypes or "Repeater" in node.busTypes:
                relevant.append(node)
        return relevant

    def ctf_dic_pop(self, egraphs):
        for indi in egraphs:
            egraph = egraphs[indi]
            tx = egraph.get_TX()
            for n in egraph._getNodes():
                if n != tx and (n.energyEdgesOut != [] or n.energyEdgesIn != []):
                    pathinput = egraph.shortestPath_NodeCount(tx, n)
                    path = egraph.convertNodePath2EdgePath(pathinput)
                    new_ctf_data = egraph.calcCTF(path)
                    self.ctf[(tx.name, n.name)] = new_ctf_data
                    self.ctf[(n.name, tx.name)] = new_ctf_data
        return