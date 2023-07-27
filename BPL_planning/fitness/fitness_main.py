import sys

sys.path.append('./')
import statistics as stat

from graphs.RoutingGraph import RoutingGraph
from load_data import load_netconfig
from calculations import snr_bottleneck


def get_fitness_multi(eGraph, individual, file, function, impedance, config=""):
    load_netconfig.auto_generate_netconfig(eGraph)
    eGraph.place_repeater(individual)
    rGraph = RoutingGraph(eGraph, 1e-09, 1e-05)
    egraphs = load_netconfig.generate_eGraph_array_with_repeaters(individual, file, function, impedance)
    eGraph.ctf_dic_pop(egraphs)

    return (snr_bottleneck.bottleneck(rGraph)), len(eGraph.get_Repeater())


def get_fitness_alt(eGraph, individual, file, function, impedance, noisefloor, config=""):
    egraphs = load_netconfig.generate_eGraph_array_with_repeaters(individual, file, function, impedance)

    load_netconfig.auto_generate_netconfig(eGraph)
    eGraph.place_repeater(individual)
    rGraph = RoutingGraph(eGraph, noisefloor, 1e-5)  # Graph, Noisefloor, TXPSD
    rGraphs = {}

    for key, val in egraphs.items():
        rGraphs[key] = RoutingGraph(val, noisefloor, 1e-5)

    # snr, data= snr_bottleneck.bottleneck_alt(rGraph,rGraphs,egraphs)
    # snr, data = snr_bottleneck.mean_snr(rGraph,rGraphs,egraphs)
    mean_snr, min_snr, d_mean, d_min = snr_bottleneck.bottleneck_tdma_syn(rGraph, rGraphs, egraphs)
    dict, data_rates = rGraph.tdmaAsynch_sp_multi_tx()
    data = stat.mean(data_rates)
    return (mean_snr, data, len(eGraph.get_Repeater()))
