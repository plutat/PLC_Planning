import imp
import networkx as nx
import math
import statistics as stat
from calculations import dataRates
from joblib import Parallel, delayed
import numpy as np


# deprecated builds a tree and searches for best solution
def bottleneck(routing_graph) -> float:
    snr_matrix = routing_graph.calcSNRMatrix()
    start_g = baseGraph(routing_graph, snr_matrix)
    rx_list = routing_graph.get_RX()
    tx = routing_graph.get_TX()
    repeaters = routing_graph.get_Repeater()
    snr_bottleneck_list = []
    for rx in rx_list:
        temp_G = start_g.copy()
        tweight = snr_matrix[(tx.name, rx.name)]
        temp_G.add_edge(tx.name, rx.name, weight=tweight)
        for r in repeaters:
            if (r != rx):
                tweight = snr_matrix[(r.name, rx.name)]
                temp_G.add_edge(r.name, rx.name, weight=tweight)
        edges = sorted(temp_G.edges(data=True), key=lambda t: t[2].get('weight', 1), reverse=False)
        bottle = True
        while bottle and len(edges) > 0:
            edge = edges.pop(0)
            temp_G.remove_edge(edge[0], edge[1])
            if not (nx.is_connected(temp_G)):
                bottle = False
                sub_graphs = nx.connected_components(temp_G)
                for s in sub_graphs:
                    if rx.name in s and tx.name in s:
                        bottle = True

        snr_bottleneck_list.append(edge[2]["weight"])
    return min(snr_bottleneck_list)


def bottel_alt_par(edge, eGraphs, rGraphs):
    eGraph = eGraphs[edge.startNode.name]
    r2Graph = rGraphs[edge.startNode.name]
    for node in eGraph._getNodes():
        if node.name == edge.startNode.name:
            start = node
        if node.name == edge.endNode.name:
            end = node

    pathinput = eGraph.shortestPath_NodeCount(start, end)
    path = eGraph.convertNodePath2EdgePath(pathinput)

    snr_array = r2Graph.calcSNR_ofPath(path)
    # data.append(dataRates.calculateDataRate(snr_array))
    snr_in_mW = stat.mean(snr_array)
    snrRate = (10 * (math.log10(snr_in_mW / 1000))) + 30

    return (snrRate)


# currently used implementation
def bottleneck_tdma_syn(rGraph, rGraphs, eGraphs):
    rates = []
    data = []
    edges = rGraph._getEdges()
    # turns out using more than 1 slows down the execution

    for edge in edges:
        eGraph = eGraphs[edge.startNode.name]
        r2Graph = rGraphs[edge.startNode.name]
        for node in eGraph._getNodes():
            if node.name == edge.startNode.name:
                start = node
            if node.name == edge.endNode.name:
                end = node

        pathinput = eGraph.shortestPath_NodeCount(start, end)
        path = eGraph.convertNodePath2EdgePath(pathinput)

        snr_array = r2Graph.calcSNR_ofPath(path)
        # data.append(dataRates.calculateDataRate(snr_array))
        snr_mean = stat.mean(snr_array)

        data.append(dataRates.ofdmDataRate(snr_array))
        snrRate = (10 * (math.log10(snr_mean)))

        rates.append(snrRate)

    # d=(min((np.array(data))/len(rGraph.get_Agents())))
    d_mean = (stat.mean((np.array(data)) / len(rGraph.get_Agents())))
    d_min = (min((np.array(data)) / len(rGraph.get_Agents())))

    return stat.mean(rates), min(rates), d_mean, d_min


def bottleneck_tdma_syn_sp(rGraph, rGraphs, eGraphs):
    rates = []
    data = []
    edges = rGraph._getEdges()
    # turns out using more than 1 slows down the execution

    for edge in edges:
        eGraph = eGraphs[edge.startNode.name]
        r2Graph = rGraphs[edge.startNode.name]
        for node in eGraph._getNodes():
            if node.name == edge.startNode.name:
                start = node
            if node.name == edge.endNode.name:
                end = node

        pathinput = eGraph.shortestPath_NodeCount(start, end)
        path = eGraph.convertNodePath2EdgePath(pathinput)

        snr_array = r2Graph.calcSNR_ofPath(path)
        # data.append(dataRates.calculateDataRate(snr_array))
        snr_in_mW = stat.mean(snr_array)
        data.append(dataRates.calculateDataRate3(snr_array) / len(pathinput))
        snrRate = (10 * (math.log10(snr_in_mW / 1000))) + 30

        rates.append(snrRate)

    return (stat.mean(data), min(rates), stat.mean(data), min(data))


def mean_snr(rGraph, rGraphs, eGraphs):

    rates = []
    data = []
    edges = rGraph._getEdges()


    for edge in edges:
        eGraph = eGraphs[edge.startNode.name]
        r2Graph = rGraphs[edge.startNode.name]
        for node in eGraph._getNodes():
            if node.name == edge.startNode.name:
                start = node
            if node.name == edge.endNode.name:
                end = node

        pathinput = eGraph.shortestPath_NodeCount(start, end)
        path = eGraph.convertNodePath2EdgePath(pathinput)

        snr_array = r2Graph.calcSNR_ofPath(path)
        # data.append(dataRates.calculateDataRate(snr_array))
        snr_in_mW = stat.mean(snr_array)
        data.append(dataRates.calculateDataRate3(snr_array))
        snrRate = (10 * (math.log10(snr_in_mW / 1000))) + 30

        rates.append(snrRate)
    mean = sum(rates) / len(rates)
    # bottleneck = min(rates)
    d = (min((np.array(data)) / len(rGraph.get_Agents())))

    # return (bottleneck, d)
    return (mean, d)


def baseGraph(routing_graph, weights):
    G = nx.Graph()
    tx = routing_graph.get_TX()
    repeaters = routing_graph.get_Repeater()
    for start_node in repeaters:
        tweight = weights[(tx.name, start_node.name)]
        G.add_edge(tx.name, start_node.name, weight=tweight)
        for end_node in repeaters:
            if end_node != start_node:
                tweight = weights[(start_node.name, end_node.name)]
                G.add_edge(end_node.name, start_node.name, weight=tweight)

    return G