#start a complete network planning
import pickle

from load_data import xml_to_eGraph
from load_data import pkl_to_eGraph
from load_data import load_netconfig
from strategies import tabu

#grid_file = r'../files/5nodes.xml'
#function = xml_to_eGraph.xml_to_eGraph

#eGraph, line_dict_list = xml_to_eGraph.xml_to_eGraph(grid_file,50)


grid_file = r'../files/Energieversorgung Halle Netz GmbH_120.p'
function = pkl_to_eGraph.pkl_to_eGraph

eGraph, line_dict_list = pkl_to_eGraph.pkl_to_eGraph(grid_file)


load_netconfig.auto_generate_netconfig(eGraph)
eGraph.add_edges(line_dict_list)
load_netconfig.auto_generate_netconfig(eGraph)

#best_sol, best_dic = tabu.tabuSearch(35, eGraph, grid_file, function, 50, 50, neigh_count=16, p1=40, p2=40, p3=15,
#               p4=15)
best_sol, best_dic = tabu.tabuSearch(30,eGraph,grid_file,function,50,50,1e-10,50)

print(best_sol)
print(best_dic)

with open('../files/testtest'+ '.pickle',
          'wb') as handle:
    pickle.dump(best_dic, handle, protocol=pickle.HIGHEST_PROTOCOL)
print("DONE")
