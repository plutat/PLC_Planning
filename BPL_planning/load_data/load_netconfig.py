import xmltodict
from fitness import repeater_on_kvs
from graphs import EnergyGraph
from load_data import json_to_eGraph
import json

default_numbands = 5
default_txpsd = 1e-8
default_kleinste_freq = 1000.0
default_hoechste_freq = 10000000.0
default_noise_floor = 1e-9


# load config data from xml and adds to existintg eGraph
def xml_to_netconfig(eGraph, configFile, Tx=None):
    # print("--------->       Load Config from .xml")
    with open(configFile) as configfile:
        tempdoc = xmltodict.parse(configfile.read())

    nodes = eGraph._getNodes()
    leafs = eGraph._getLeafs()

    if Tx == None:
        for tx in tempdoc["root"]["Tx"]:
            if tx == "@type":
                continue
            for node in nodes:
                if node.name == str(tempdoc["root"]["Tx"][tx]).partition("n")[2]:
                    node.addBusType("Tx")
                else:
                    continue

        for rx in tempdoc["root"]["Rx"]:
            if rx == "@type":
                continue
            for node in nodes:
                if node.name == str(tempdoc["root"]["Rx"][rx]).partition("n")[2]:
                    node.addBusType("Rx")
                else:
                    continue

    else:
        # print("Leafs: ", leafs)
        for node in nodes:
            if node.name == Tx.name:
                node.addBusType("Tx")

            for leaf in leafs:
                if node.name == leaf.name:
                    node.addBusType("Rx")

    for impedance in tempdoc["root"]["custom_impedances"]:
        for node in nodes:
            if node.name == impedance[1]:
                node.setzShunt(float(tempdoc["root"]["custom_impedances"][impedance]))
            else:
                continue


# generates config Data for net (TX and RXs)
def auto_generate_netconfig(eGraph, Tx=None):
    nodes = eGraph._getNodes()
    leafs = eGraph._getLeafs()

    for node in nodes:
        if Tx == None:
            # print(node.name)
            node_name = int(node.name)
            if node_name == 1:
                # print(node.name)
                node.addBusType("Tx")
        else:
            if node.name == Tx.name:
                node.addBusType("Tx")

        for leaf in leafs:
            if node.name == leaf.name:
                node.addBusType("Rx")


def init_supplytaskRX(eGraph, Rx="leafs", netconfig_json=None):
    nodes = eGraph._getNodes()
    leafs = eGraph._getLeafs()

    if netconfig_json is not None:
        with open(netconfig_json) as read_file:
            netconfig = json.load(read_file)
        RX_names = netconfig["RX_names"]

        for node in nodes:
            if node.name in RX_names:
                node.addBusType("RX")

    for node in nodes:
        if Rx == None:  ##TODO: interpret undefined supplytask
            # print(node.name)
            node_name = int(node.name)

        elif Rx == "leafs":
            for leaf in leafs:
                if node.name == leaf.name:
                    node.addBusType("Rx")


def init_supplytaskTX(eGraph, Tx=None, netconfig_json=None):
    nodes = eGraph._getNodes()
    # leafs = eGraph._getLeafs()

    if netconfig_json is None:
        for node in nodes:
            if Tx == None:
                # print(node.name)
                node_name = int(node.name)
                if node_name == 1:
                    # print(node.name)
                    node.addBusType("Tx")
            else:
                if node.name == Tx.name:
                    node.addBusType("Tx")
    else:
        with open(netconfig_json) as read_file:
            netconfig = json.load(read_file)

        TX_names = netconfig["TX_names"]

        for node in nodes:
            if node.name in TX_names:
                node.addBusType("TX")


def generate_eGraph_array(file, function, config=None):
    if config != None:
        eGraph, line_dict_list = function(file)
        xml_to_netconfig(eGraph, config)
        EnergyGraph.EnergyGraph.add_edges(eGraph, line_dict_list)
        # eGraph.plot()
    else:
        eGraph, line_dict_list = function(file)
        auto_generate_netconfig(eGraph)
        EnergyGraph.EnergyGraph.add_edges(eGraph, line_dict_list)
        auto_generate_netconfig(eGraph)
        # eGraph.plot()

    repeater_on_kvs.set_repeater(eGraph)
    nodes = eGraph._getNodes()
    routableNodes = list()
    energyGraphs = dict()

    for node in nodes:
        # print(node.name, "  ", node.busTypes)
        if node.isRoutable():
            routableNodes.append(node)

    for routableNode in routableNodes:
        if config != None:
            eGraph, line_dict_list = function(file)
            xml_to_netconfig(eGraph, config, routableNode)
            EnergyGraph.EnergyGraph.add_edges(eGraph, line_dict_list)
            xml_to_netconfig(eGraph, config, routableNode)
            repeater_on_kvs.set_repeater(eGraph)
            energyGraphs[routableNode.name] = eGraph
            # eGraph.plot()
        else:
            eGraph, line_dict_list = function(file)
            auto_generate_netconfig(eGraph, routableNode)
            EnergyGraph.EnergyGraph.add_edges(eGraph, line_dict_list)
            auto_generate_netconfig(eGraph, routableNode)
            repeater_on_kvs.set_repeater(eGraph)
            energyGraphs[routableNode.name] = eGraph
            # eGraph.plot()

    return energyGraphs


def generate_eGraph_array_with_repeaters(individual, file, function, grid_config, config=None):
    if config != None:
        eGraph, line_dict_list = function(file, grid_config)
        xml_to_netconfig(eGraph, config)
        EnergyGraph.EnergyGraph.add_edges(eGraph, line_dict_list)
        # eGraph.plot()
    else:
        eGraph, line_dict_list = function(file, grid_config)
        auto_generate_netconfig(eGraph)
        EnergyGraph.EnergyGraph.add_edges(eGraph, line_dict_list)
        auto_generate_netconfig(eGraph)
        # eGraph.plot()
    eGraph.place_repeater(individual)
    repeater_on_kvs.set_repeater(eGraph)
    nodes = eGraph._getNodes()
    routableNodes = list()
    energyGraphs = dict()
    t = eGraph.get_Potential()
    indi_dic = {}
    for x in range(len(t)):
        indi_dic[t[x].name] = individual[x]
    for node in nodes:
        # print(node.name, "  ", node.busTypes)
        if node.isRoutable():
            routableNodes.append(node)
    per = len(routableNodes)

    i = 0
    for routableNode in routableNodes:
        i = i + 1

        if config != None:
            if function == json_to_eGraph.json_to_eGraph:
                eGraph, line_dict_list = function(file, grid_config)
                xml_to_netconfig(eGraph, config, routableNode)
                EnergyGraph.EnergyGraph.add_edges(eGraph, line_dict_list)
                xml_to_netconfig(eGraph, config, routableNode)
                eGraph.place_repeater_alt(indi_dic)
                repeater_on_kvs.set_repeater(eGraph)
                energyGraphs[routableNode.name] = eGraph
            else:
                eGraph, line_dict_list = function(file, grid_config)
                auto_generate_netconfig(eGraph, routableNode)
                EnergyGraph.EnergyGraph.add_edges(eGraph, line_dict_list)
                auto_generate_netconfig(eGraph, routableNode)
                eGraph.place_repeater(individual)
                repeater_on_kvs.set_repeater(eGraph)
                energyGraphs[routableNode.name] = eGraph
            # eGraph.plot()
        else:
            if function == json_to_eGraph.json_to_eGraph:
                eGraph, line_dict_list = function(file, grid_config)
                auto_generate_netconfig(eGraph, routableNode)
                EnergyGraph.EnergyGraph.add_edges(eGraph, line_dict_list)
                auto_generate_netconfig(eGraph, routableNode)
                eGraph.place_repeater_alt(indi_dic)
                repeater_on_kvs.set_repeater(eGraph)
                energyGraphs[routableNode.name] = eGraph
            else:
                eGraph, line_dict_list = function(file, grid_config)
                auto_generate_netconfig(eGraph, routableNode)
                EnergyGraph.EnergyGraph.add_edges(eGraph, line_dict_list)
                auto_generate_netconfig(eGraph, routableNode)
                eGraph.place_repeater(individual)
                repeater_on_kvs.set_repeater(eGraph)
                energyGraphs[routableNode.name] = eGraph
            # eGraph.plot()

    return energyGraphs
