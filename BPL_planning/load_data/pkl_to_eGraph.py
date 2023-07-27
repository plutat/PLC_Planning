from graphs.EnergyGraph import EnergyGraph
from graphs import EnergyEdge
from graphs import Node
import pandapower.plotting as pandaplt
import matplotlib.pyplot as plt
import numpy as np
import pandapower as pp

def pkl_to_eGraph(pklfile, print = False): #converts pkl file into an eGraph
#def pkl_to_eGraph(pklfile, impedance, print = False): #converts pkl file into an eGraph

    #impedance = 50
    INDEX = 0
    NAME = 0
    X_COORD = 1
    Y_COORD = 2
    F_BUS = 1
    T_BUS = 2
    WEIGHT = 0
    TYPE = 0
    net = pp.from_pickle(pklfile)
    eGraph = EnergyGraph()
    # reading bus information
    bus_table = net["bus"]
    Idx_pv = net.sgen.loc[net.sgen.type.str.contains("PV").fillna(False)].index
    bus_pv = (net.sgen['bus'].loc[Idx_pv]).tolist()
    # reading coordinates and saving them in bus_parameter
    bus_geodata = net["bus_geodata"]
    n = bus_table.shape[0]
    bus_parameter = np.zeros((n, 1), np.dtype(object))
    bus_indices = np.zeros((n, 3), dtype=np.float)
    bus_indices[:, INDEX] = bus_table.index - 1000000
    bus_parameter[:, NAME] = bus_table.name.values
    bus_indices[:, X_COORD] = (bus_geodata.x.values) * 1000  # convert from km into m
    bus_indices[:, Y_COORD] = (bus_geodata.y.values) * 1000

    for b_idx, b_p in zip(bus_indices, bus_parameter): #add all nodes to eGraph
        ''' 
        if int(b_idx[INDEX]) in bus_pv:
            #b_p[NAME]: Pv_anschluss = True
        else:
            #b_p[NAME]: Pv_anschluss = False
        '''
        newNode = Node.Node(eGraph.getUniqueId(), posX=b_idx[X_COORD], posY=b_idx[Y_COORD], zShunt=impedance, name=str(int(b_idx[INDEX])))
        eGraph._addNode(newNode)

    nodes = eGraph._getNodes()

    # reading lines information
    line_table = net["line"]
    m = line_table.shape[0]
    line_indices = np.zeros((m, 3), dtype=np.int)
    line_type = np.zeros((m, 1), np.dtype(object))
    line_parameter = np.zeros((m, 1), dtype=np.float)
    line_parameter[:, WEIGHT] = line_table.length_km.values
    line_type[:, TYPE] = line_table.std_type.values
    line_indices[:, INDEX] = line_table.index
    line_indices[:, F_BUS] = line_table.from_bus.values
    line_indices[:, T_BUS] = line_table.to_bus.values

    line_dict_list = []

    for l_idx, l_p, l_t in zip(line_indices, line_parameter, line_type): #safe lines in line_dict_list
        fromNodeStr = str(l_idx[F_BUS]-1000000)
        toNodeStr = str(l_idx[T_BUS]-1000000)
        cable_type = str(l_t[TYPE])

        line_dict = { #one line_dict for every line in pkl
            "from_bus": {},
            "to_bus": {},
            "line_type": {}
        }

        line_dict["from_bus"] = fromNodeStr
        line_dict["to_bus"] = toNodeStr
        line_dict["line_type"] = cable_type

        line_dict_list.append(line_dict)

    if print == True:
        # plotting the networks with IDs
        # creae separate collections for buses, lines, trafos etc...
        bc = pandaplt.create_bus_collection(net, net.bus.index, size=0.00002, color="powderblue", zorder=1)
        lcd = pandaplt.create_line_collection(net, net.line.index, color="grey", linewidths=0.5, use_bus_geodata=True, zorder=2)
        tlc, tpc = pandaplt.create_trafo_collection(net, net.trafo.index, color="g", size=0.000005)
        sc = pandaplt.create_bus_collection(net, net.ext_grid.bus.values, patch_type="rect", size=0.000006, color="lightyellow", zorder=11)
        bus_num = [str(a) for a in (net.bus.index)]
        bus_geodata = net["bus_geodata"]
        buses = np.copy(net.bus.index.values)
        coords = list(zip(bus_geodata.loc[buses, "x"].values, bus_geodata.loc[buses, "y"].values))
        ac = pandaplt.create_annotation_collection(bus_num, coords, size=0.0000095)
        # Draw all the collected plots
        pandaplt.draw_collections([lcd, bc, tlc, tpc, sc, ac])
        plt.show()

    return eGraph, line_dict_list