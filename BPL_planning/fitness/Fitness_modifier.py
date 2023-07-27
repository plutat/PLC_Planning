import numpy

import load_data.load_netconfig
from fitness import fitness_main
from graphs.RoutingGraph import RoutingGraph
from graphs.EnergyGraph import EnergyGraph
from calculations import snr_bottleneck
import json
class Fitness_modifier():

    __snr_tpyes: str
    __data_rate_types: str
    __repeating_types: str

    __eGraph: EnergyGraph
    __line_dict_list: list
    __file: str
    __grid_config: str
    #__function:

    __noisefloor: float
    __txpsd: float

    __impedance_list: list
    __passive_leaf_shunt: float
    __modem_leaf_shunt: float
    __global_modem_impedance: float
    __passive_shunts: float
    __global_shunt: float

    __min_f: float
    __max_f: float
    __notches: list
    __carrier_bw: float

    __spectral_eff: float

    __c_capex: float
    __c_opex: float

    @property
    def grid_config(self) -> str:
        return self.__grid_config
    @property
    def snr_types(self) -> str:
        return self.__snr_tpyes
    @property
    def data_rate_types(self) -> str:
        return self.__data_rate_types
    @property
    def repeating_types(self) -> str:
        return self.__repeating_types
    @property
    def eGraph(self) -> EnergyGraph:
        return self.__eGraph
    @property
    def line_dict_list(self) -> list:
        return self.__line_dict_list
    @property
    def file(self) -> str:
        return self.__file
    @property
    def impedance_list(self) -> list:
        return self.__impedance_list
    @property
    def passive_leaf_shunt(self) -> float:
        return self.__passive_leaf_shunt
    @property
    def modem_leaf_shunt(self) -> float:
        return self.__modem_leaf_shunt
    @property
    def global_modem_impedance(self) -> float:
        return self.__global_modem_impedance
    @property
    def passive_shunts(self) -> float:
        return self.__passive_shunts
    @property
    def global_shunt(self) -> float:
        return self.__global_shunt
    @property
    def min_f(self) -> float:
        return self.__min_f
    @property
    def max_f(self) -> float:
        return self.__max_f
    @property
    def notches(self) -> list:
        return self.__notches
    @property
    def carrier_bw(self) -> float:
        return self.__carrier_bw
    @property
    def spectral_eff(self) -> float:
        return self.__spectral_eff
    @property
    def c_opex(self) -> float:
        return self.__c_opex
    @property
    def c_capex(self) -> float:
        return self.__c_capex

    @property
    def noisefloor(self) -> float:
        return self.__noisefloor

    @property
    def txpsd(self) -> float:
        return self.__txpsd

    #def __init__(self, eGraph,individual,file,function,config=""):
    #def __init__(self, eGraph, individual, file, function, config=""):
    def __init__(self, grid_file, read_function, grid_config):
        self.__snr_types = ''
        self.__data_rate_types = ''
        self.__repeating_types = ''
        self.__noisefloor = 1e-11
        self.__txpsd = 1e-5
        #self.__eGraph = eGraph
        self.__grid_config = grid_config
        self.__eGraph, self.__line_dict_list = read_function(grid_file, grid_config)
        #self.__individual = individual
        self.__file = grid_file
        self.__function = read_function
        #self.__config = config

    def quick_init(self, grid_config=None, comm_config=None, config=None):
        if grid_config is not None:
            self.load_grid_config(grid_config)

        if comm_config is not None:
            self.load_comm_config(comm_config)

        if config is not None:
            self.load_config(config)

    def load_config(self, configfile: str):

        with open(configfile) as json_file:
            data = json.load(json_file)

        self.__noisefloor = data['noisefloor']
        self.__txpsd = data['txpsd']
        self.__globalShuntImpedance = data['globalShuntImpedance']
        self.__modemImpedance = data['modemImpedance']
        self.__leafImpedance = data['leafImpedance']
        self.__c_capex = data['c_capex']
        self.__c_opex = data['c_opex']

    def load_grid_config(self, configfile: str):

        with open(configfile) as json_file:
            data = json.load(json_file)

        self.__impedance_list = data['impedance_list']
        self.__passive_leaf_shunt = data['passive_leaf_shunt']
        self.__modem_leaf_shunt = data['modem_leaf_shunt']
        self.__global_modem_impedance = data['global_modem_impedance']
        self.__passive_shunts = data['passive_shunts']
        self.__global_shunt = data['global_shunt']

    def load_comm_config(self, configfile: str):

        with open(configfile) as json_file:
            data = json.load(json_file)

        self.__min_f = data['min_f']
        self.__max_f = data['max_f']
        self.__notches = data['notches']
        self.__carrier_bw = data['carrier_bw']
        self.__spectral_eff = data['spectral_eff']

        self.__c_capex = data['c_capex']
        self.__c_opex = data['c_opex']


    def calculate_metrics(self, eGraph, line_dict, individual):

        metrics = ['datarate, costs']
        fitness_values= {'mean_snr':0, 'min_snr':0, 'mean_datarate_asynch':0, 'min_datarate_asynch':0, 'mean_datarate_synch':0, 'min_datarate_synch':0, 'num_repeaters':0}


        #fitness_main.load_netconfig.auto_generate_netconfig(self.__eGraph)
        self.__eGraph.place_repeater(individual)
        #rGraph = RoutingGraph(self.__eGraph, self.__noisefloor, self.__txpsd)
        rGraph = RoutingGraph(self.__eGraph)

        egraphs = fitness_main.load_netconfig.generate_eGraph_array_with_repeaters(individual, self.__file, self.__function, self.__grid_config) ##TODO: Warum das auch?
        self.__eGraph.ctf_dic_pop(egraphs)

        rGraphs = {}
        for key, val in egraphs.items():
            #rGraphs[key] = RoutingGraph(val, noisefloor, txpsd)
            rGraphs[key] = RoutingGraph(val)

        snr_mean, snr_min, data_mean, data_min = snr_bottleneck.bottleneck_tdma_syn(rGraph, rGraphs, egraphs)

        if 'data_rate' in metrics:
            tdma_dict, datarate_list = rGraph.tdmaAsynch_sp_multi_tx()
            fitness_values['mean_datarate_asynch'] = sum(datarate_list) / len(datarate_list)
            fitness_values['min_datarate_asynch'] = min(datarate_list)

        fitness_values['mean_snr'] = snr_mean
        fitness_values['min_snr'] = snr_min

        fitness_values['mean_datarate_synch'] = data_mean
        fitness_values['min_datarate_synch'] = data_min

        if 'costs' in metrics:
            fitness_values['num_repeaters'] = len(self.__eGraph.get_Repeater())
            fitness_values['costs_capex'] = fitness_values['num_repeaters'] * self.__c_capex
            fitness_values['costs_opex'] = fitness_values['num_repeaters'] * self.__c_opex

        return fitness_values

    def connect_eGraph(self, Rx, Tx, net_config):
        load_data.load_netconfig.init_supplytaskTX(self.eGraph, Tx,net_config)
        self.eGraph.add_edges(self.line_dict_list)
        load_data.load_netconfig.init_supplytaskRX(self.eGraph, Rx,net_config)

    @noisefloor.setter
    def noisefloor(self, value):
        self._noisefloor = value

