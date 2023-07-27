import json
from graphs import EnergyGraph
from graphs import EnergyEdge
from graphs import Node


def json_to_eGraph(jasonfile, grid_config):  # converts json file into an eGraph
    with open(jasonfile) as read_file:
        tempdata = json.load(read_file)

    with open(grid_config) as read_file:
        grid_config_data = json.load(read_file)

    if grid_config_data['impedance_setting'] == 'global':
        impedance = grid_config_data['global_shunt']

    eGraph = EnergyGraph.EnergyGraph()

    nodenumber = 0
    for node in tempdata["bus"]:  # read and add all nodes to eGraph
        # print("coordinate", tempdoc["root"]["GeneratedCoordinates"][node])
        # print("Node", node.partition("n")[2])
        name = tempdata["bus"][nodenumber]["busID"]  # TODO Als int gespeichert, wenn als str = Fehlermeldung
        X = float(tempdata["bus"][nodenumber]["x"])
        Y = float(tempdata["bus"][nodenumber]["y"])
        Node_has_PV = False
        MSLINK_Anschluss = tempdata["bus"][nodenumber]["MSLINK_Anschluss"]
        MSLINK_KVS = tempdata["bus"][nodenumber]["MSLINK_KVS"]
        MSLINK_Einspeiser = tempdata["bus"][nodenumber]["MSLINK_Einspeiser"]
        if MSLINK_Einspeiser:
            Node_has_PV = True

        zShunt = impedance

        newNode = Node.Node(eGraph.getUniqueId(), posX=X, posY=Y, zShunt=zShunt, name=name,
                            kvs=[MSLINK_KVS, MSLINK_Anschluss, MSLINK_Einspeiser])

        eGraph._addNode(newNode)
        nodenumber += 1

    nodes = eGraph._getNodes()

    line_dict_list = []
    linenumber = 0
    for line in tempdata["branch"]:  # read all lines and safe in line_dict_list
        fromNodeStr = tempdata["branch"][linenumber]["from_busID"]
        toNodeStr = tempdata["branch"][linenumber]["to_busID"]
        lineType = tempdata["branch"][linenumber]["branchType"]
        # print(lineType)
        MSLINK = tempdata["branch"][linenumber]["MSLINK"]

        line_dict = {  # one line_dict for every line in json
            "from_bus": {},
            "to_bus": {},
            "line_type": {},
            "MSLINK": {},
            "lenght": {}
        }

        line_dict["from_bus"] = fromNodeStr
        line_dict["to_bus"] = toNodeStr
        line_dict["line_type"] = lineType
        line_dict["MSLINK"] = MSLINK
        line_dict["length"] = tempdata["branch"][linenumber]["Length"]

        line_dict_list.append(line_dict)

        linenumber += 1

    return eGraph, line_dict_list