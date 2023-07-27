from cProfile import label
# from graphviz import Digraph
from graphs.Graph import Graph
import networkx
import random
import matplotlib.pyplot as plt
import uuid
from graphs.Node import Node
from graphs.Edge import Edge


class Graph_NetworkX(Graph):
    __nxGraph: networkx.DiGraph

    def __init__(self) -> None:
        super().__init__()
        self.__nxGraph = networkx.DiGraph()

    def _shortestPath(self, startnode: Node, endnode: Node) -> list:
        return networkx.shortest_path(self.__nxGraph, startnode, endnode)

    def _addNode(self, node: Node):
        # TODO: Check if id is unique
        self.__nxGraph.add_node(node)

    def _addEdge(self, edge: Edge):
        # TODO: Check if id is unique
        # edge.startNode.energyEdgesOut.append(edge)
        self.__nxGraph.add_edge(edge.startNode, edge.endNode, obj=edge)

    def _getEdges(self):
        return [tup[2]["obj"] for tup in self.__nxGraph.edges(data=True)]

    def _hasEdge(self, edge) -> bool:
        return self.__nxGraph.has_edge(*edge)

    def _getNodes(self):
        return self.__nxGraph.nodes

    def _removeEdges(self, edges):
        for edge in edges:
            if self.__nxGraph.has_edge((edge.startNode, edge.endNode)):
                self.__nxGraph.remove_edge((edge.startNode, edge.endNode))
        return

    def getUniqueId(self) -> uuid.UUID:
        # IMPORTANT: #return 0 #! If Id not used, set to 0 for performance reasos
        # generate a unique id
        id = uuid.uuid4()
        notFound = True
        while notFound:
            notFound = False
            for node in self.__nxGraph:
                if node.id == id:
                    notFound = True
            # TODO: check edge ids

        return id

    def getNeighbourNodes(self, node: Node, range: int):
        resultList = []
        workingList = []
        self.__nxGraph.neighbors(node)

    def getNeighbourEdges(self, node: Node, range: int):
        pass

    def getpredecessors(self, node: Node):
        self.__nxGraph.predecessors(node)

    def plot(self):
        pos = self.__hierarchy_pos(self.__nxGraph)

        nodeLabels = {}
        for node in self.__nxGraph:
            nodeLabels[node] = str(node.name) + str(node.busTypes)

        edgeLabels = {}
        for edge in self._getEdges():
            if (hasattr(edge, 'currDataRateLoad')):
                edgeLabels[(edge.startNode, edge.endNode)] = str(edge.currDataRateLoad)

        networkx.draw(self.__nxGraph, labels=nodeLabels, pos=pos, with_labels=True)
        networkx.draw_networkx_edge_labels(self.__nxGraph, pos=pos, edge_labels=edgeLabels)

        # plt.savefig('hierarchy.png')
        plt.show()

    def __hierarchy_pos(self, G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):

        '''
        From Joel's answer at https://stackoverflow.com/a/29597209/2966723.
        Licensed under Creative Commons Attribution-Share Alike

        If the graph is a tree this will return the positions to plot this in a
        hierarchical layout.

        G: the graph (must be a tree)

        root: the root node of current branch
        - if the tree is directed and this is not given,
        the root will be found and used
        - if the tree is directed and this is given, then
        the positions will be just for the descendants of this node.
        - if the tree is undirected and not given,
        then a random choice will be used.

        width: horizontal space allocated for this branch - avoids overlap with other branches

        vert_gap: gap between levels of hierarchy

        vert_loc: vertical location of root

        xcenter: horizontal location of root
        '''
        # if not networkx.is_tree(G):
        #     raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

        if root is None:
            if isinstance(G, networkx.DiGraph):

                for node in networkx.topological_sort(G):
                    if len(G.out_edges(node)) != 0:
                        root = node
                        break

            else:
                root = random.choice(list(G.nodes))

        def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
            '''
            see hierarchy_pos docstring for most arguments

            pos: a dict saying where all nodes go if they have been assigned
            parent: parent of this branch. - only affects it if non-directed

            '''

            if pos is None:
                pos = {root: (xcenter, vert_loc)}
            else:
                pos[root] = (xcenter, vert_loc)
            children = list(G.neighbors(root))
            if not isinstance(G, networkx.DiGraph) and parent is not None:
                children.remove(parent)
            if len(children) != 0:
                dx = width / len(children)
                nextx = xcenter - width / 2 - dx / 2
                for child in children:
                    nextx += dx
                    pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                         vert_loc=vert_loc - vert_gap, xcenter=nextx,
                                         pos=pos, parent=root)
            return pos

        hierarchy_pos = _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

        posX = 0
        isolatedNodes = list(filter(lambda node: node not in hierarchy_pos, G))
        for node in isolatedNodes:
            hierarchy_pos[node] = [posX, 0]
            posX += width / ((len(isolatedNodes) + 1) * 2)

        return hierarchy_pos

    # returns a list of all nodes of the net
    def _getLeafs(self):
        leaf_nodes = [node for node in self.__nxGraph.nodes if
                      self.__nxGraph.in_degree(node) != 0 and self.__nxGraph.out_degree(node) == 0]
        return leaf_nodes

    def _isTree(self):
        isTree = networkx.is_tree(self.__nxGraph)
        return isTree