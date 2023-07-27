from fitness import Fitness_modifier as fm
from strategies import nsga3_off
from load_data import json_to_eGraph

data_path = r'..\plc_planning_tool\files'


comm_config = data_path + '\comm_config.json'
#grid_file = data_path + '\example_grid_struct.json'
grid_config = data_path + '\grid_config.json'

read_function = json_to_eGraph.json_to_eGraph

e_Graph, line_dict_list = read_function(grid_file, grid_config)
noises = [1e-10, 1e-11, 1e-12]

for noisefloor in noises:

    fitness = fm.Fitness_modifier(grid_file, read_function, grid_config)
    fitness.quick_init(grid_config, comm_config)
    fitness.connect_eGraph(Rx ="leafs", Tx = None ,net_config = None)

    #fitness.overwrite_noisefloor(noisefloor)
    fitness.noisefloor = noisefloor

    pop, logbook, best_result = nsga3_off.nsga3_core(400, e_Graph, line_dict_list, fitness)

    print(best_result)