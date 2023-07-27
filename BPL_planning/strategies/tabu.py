from ast import If
from distutils.command.config import config
from optparse import Values
from pickle import APPEND
from re import A
import sys
from typing import no_type_check_decorator

import fitness

sys.path.append('./')
import time
# Test for a parallaized bruteforce approach + printing results in txt file
from fitness import fitness_main as ff
import networkx as nx
import itertools
from joblib import Parallel, delayed
import random

from graphs.RoutingGraph import RoutingGraph
from graphs.EnergyGraph import EnergyGraph
from graphs.EnergyEdge import EnergyEdge
from graphs.Node import Node
from load_data import xml_to_eGraph
from load_data import load_netconfig


##This will creat/update the best list
def bestList(best_dict, results):
    """

    :param best_dict:
    :param results:
    :return:
    """
    for result in results:
        if result["rep"] in best_dict:
            if base_fitness(result) > base_fitness(best_dict[result["rep"]]):
                best_dict[result["rep"]] = result.copy()

        else:
            best_dict[result["rep"]] = result.copy()

    return best_dict


## Stoping conidition for the taboo search:
def stoppingCondition(start_time, iteration, max_iterations, timer_stop):
    timer1 = int(time.time())
    if (iteration >= max_iterations):
        return 1
    else:
        return 0


## generates new neighbours to test, uses different criteria which we can change
def get_neighbours(prev_tabu, current_best, neigh_dict, amount, vertices):
    neighbours_list = []
    iter = 0
    n_test = True
    n_names = list(neigh_dict.keys())
    while len(neighbours_list) < amount / 3 and iter < amount * 2:
        tmp = current_best.copy()
        iter = iter + 1
        for i in range(len(current_best)):
            if tmp[i] == 0:
                neigh = []
                for x in neigh_dict[n_names[i]]:
                    if ("n" + str(x)) in vertices:
                        if current_best[vertices.index("n" + str(x))] == 1:
                            n_test = False
                            break
                        else:
                            n_test = True
                            neigh.append(vertices.index("n" + str(x)))
                if random.randint(0, 10) > 6:
                    if n_test and neigh != []:
                        if random.randint(0, 1):
                            tmp[i] = 1
                        else:
                            pote = random.choice(neigh)
                            if ("n" + str(pote)) in vertices:
                                tmp[vertices.index("n" + str(pote))] = 1

        if tmp not in prev_tabu:
            neighbours_list.append(tmp.copy())
            prev_tabu.append(tmp.copy())
    iter = 0
    while len(neighbours_list) < amount * 2 / 3 and iter < amount * 2:
        tmp = current_best.copy()
        iter = iter + 1

        for i in range(len(current_best)):
            if tmp[i] == 1:
                for x in neigh_dict[n_names[i]]:
                    if ("n" + str(x)) in vertices:
                        if current_best[vertices.index("n" + str(x))] == 1:

                            other = vertices.index("n" + str(x))
                            if random.randint(0, 10) > 6:
                                if random.randint(0, 1):
                                    tmp[i] = 0

                                else:
                                    tmp[other] = 0
        if tmp not in prev_tabu:
            neighbours_list.append(tmp.copy())
            prev_tabu.append(tmp.copy())

    iter = 0
    while len(neighbours_list) < amount and iter < amount * 2:
        tmp = current_best.copy()
        iter = iter + 1
        for i in range(len(current_best)):
            if tmp[i] == 1:
                for x in neigh_dict[n_names[i]]:
                    if ("n" + str(x)) in vertices:
                        if current_best[vertices.index("n" + str(x))] == 1:
                            other = vertices.index("n" + str(x))
                            if random.randint(0, 10) > 6:
                                if random.randint(0, 1):
                                    tmp[i] = 0
                                else:
                                    tmp[other] = 0
                    else:
                        neigh = []
                        for x in neigh_dict[n_names[i]]:
                            if ("n" + str(x)) in vertices:
                                if current_best[vertices.index("n" + str(x))] == 1:
                                    n_test = False
                                    break
                                else:
                                    n_test = True
                                    neigh.append(vertices.index("n" + str(x)))
                        if random.randint(0, 10) > 6:
                            if n_test and neigh != []:
                                if random.randint(0, 1):
                                    tmp[i] = 1
                                else:
                                    pote = random.choice(neigh)
                                    if ("n" + str(pote)) in vertices:
                                        tmp[vertices.index("n" + str(pote))] = 1
        if tmp not in prev_tabu:
            neighbours_list.append(tmp.copy())
            prev_tabu.append(tmp.copy())

    iter = 0
    while len(neighbours_list) < amount and iter < amount * 2:
        tmp = current_best.copy()
        iter = iter + 1
        for i in range(len(current_best)):

            if random.randint(0, 5) >= 4:
                if tmp[i] == 0:
                    tmp[i] = 1
                else:
                    tmp[i] = 0
        if tmp not in prev_tabu:
            neighbours_list.append(tmp.copy())
            prev_tabu.append(tmp.copy())

    return neighbours_list, prev_tabu


### We evaluate in a different functino so that we can call this function multiple times for parallelization
#### the parameters have to be set for each call as they otherwise might not be defined in certain threads

def evalute(individual, eGraph, file, function, noisefloor, impedance):
    eGraph, line_dict_list = function(file, impedance)
    load_netconfig.auto_generate_netconfig(eGraph)
    EnergyGraph.add_edges(eGraph, line_dict_list)
    SNR_bottleneck, data, total_repeaters = ff.get_fitness_alt(eGraph, individual, file, function, impedance,
                                                               noisefloor)
    return {"indi": individual, "snr": SNR_bottleneck, "rep": total_repeaters, "data": data}


### in This function we determin if any of the returned results are better than our current best
### this way it is easy to change the to be calulcated success
def base_fitness(value):
    wheight = [2, -1, 2]

    return (value["snr"] * wheight[0]) + (value["rep"]) * wheight[1] + (value["data"]) * wheight[2]


def compare(best_sol, neig, results):
    improve = False
    for sol in results:
        if base_fitness(sol) > base_fitness(best_sol):
            best_sol = (sol).copy()
            improve = True
    if improve:
        return best_sol, best_sol.copy()
    else:
        if base_fitness(best_sol) > base_fitness(neig):
            for sol in results:
                if base_fitness(sol) > base_fitness(neig):
                    neig = (sol).copy()
                    improve = True
            if improve:
                return best_sol, neig
        if random.randint(1, 10) > 6:
            r = random.randint(0, (len(results) - 1))
            sol = results[r]
            neig = (sol).copy()
            return best_sol, neig
    return best_sol, neig


### To create an inital solution for the Tabu search we determin the nodes with the highest degrees, we also generate a dict containing the neighbours
### neighbours will be used to generate new solution in
def tabuSearch(max_iteration, eGraph, file, function, maxTabuSize, timer_stop, noisefloor, impedance, neigh_count=16):
    vertices = list(eGraph.get_Potential())
    neigh_dict = {}
    degree = []
    for n in vertices:
        neigh_dict[n.name] = []

        if n.energyEdgesOut != []:
            for x in list(n.energyEdgesOut):
                neigh_dict[n.name].append(x._Edge__endNode.name)
        if n.energyEdgesIn != []:
            for x in list(n.energyEdgesIn):
                neigh_dict[n.name].append(x._Edge__startNode.name)
        degree.append((n, len(neigh_dict[n.name])))
    node_l = sorted(degree, key=lambda x: x[1], reverse=True)
    node_l = list(filter(lambda item: item[1] > 3, node_l))
    initial_solution = []
    if node_l != []:
        test = list(map(list, zip(*node_l)))

        for i in range(len(vertices)):
            if i in test[0]:
                initial_solution.append(1)
            else:
                initial_solution.append(0)
    else:
        for i in range(len(vertices)):
            if random.randint(1, 10) > 6:
                initial_solution.append(1)
            else:
                initial_solution.append(0)
    neighbours = []
    neighbours.append(initial_solution)
    f = []
    no = []
    for i in range(len(vertices)):
        f.append(1)
        no.append(0)
    neighbours.append(f)
    neighbours.append(no)
    results = Parallel(n_jobs=3)(delayed(evalute)(i, eGraph, file, function, noisefloor, impedance) for i in neighbours)
    iterations = 0
    start_time = int(time.time())

    print(vertices)
    ### how many parallel threads we want
    import os
    n = 16
    tabu_l = []
    best_sol = {"indi": initial_solution, "snr": results[0]["snr"], "rep": results[0]["rep"],
                "data": results[0]["data"]}
    neigh = best_sol.copy()
    best_sol, neigh = compare(best_sol, neigh, results)
    neigh = best_sol.copy()
    best_dic = {}
    while not (stoppingCondition(start_time, iterations, max_iteration, timer_stop)):
        iterations = iterations + 1

        neighbours, tabu_l = get_neighbours(tabu_l, neigh["indi"], neigh_dict, neigh_count, vertices)
        print(len(neighbours))
        print(str(iterations))
        print(best_sol)
        print(neigh)
        results = []
        results = Parallel(n_jobs=n)(
            delayed(evalute)(i, eGraph, file, function, noisefloor, impedance) for i in neighbours)
        best_sol, neigh = compare(best_sol, neigh, results)
        best_dic = bestList(best_dic, results).copy()
        if len(tabu_l) > maxTabuSize:
            d = len(tabu_l) - maxTabuSize
            del tabu_l[:d]
    print(len(tabu_l))
    return best_sol, best_dic


def tabuSearch_alt(max_iteration, eGraph, file, function, maxTabuSize, timer_stop, neigh_count=16):
    vertices = list(eGraph.get_Potential())
    neigh_dict = {}
    degree = []
    for n in vertices:
        neigh_dict[n.name] = []

        if n.energyEdgesOut != []:
            for x in list(n.energyEdgesOut):
                neigh_dict[n.name].append(x._Edge__endNode.name)
        if n.energyEdgesIn != []:
            for x in list(n.energyEdgesIn):
                neigh_dict[n.name].append(x._Edge__startNode.name)
        degree.append((n, len(neigh_dict[n.name])))
    node_l = sorted(degree, key=lambda x: x[1], reverse=True)
    node_l = list(filter(lambda item: item[1] > 3, node_l))
    initial_solution = []
    if node_l != []:
        test = list(map(list, zip(*node_l)))

        for i in range(len(vertices)):
            if i in test[0]:
                initial_solution.append(1)
            else:
                initial_solution.append(0)
    else:
        for i in range(len(vertices)):
            if random.randint(1, 10) > 6:
                initial_solution.append(1)
            else:
                initial_solution.append(0)
    neighbours = []
    neighbours.append(initial_solution)
    f = []
    no = []
    for i in range(len(vertices)):
        f.append(1)
        no.append(0)
    neighbours.append(f)
    neighbours.append(no)
    results = Parallel(n_jobs=3)(delayed(evalute)(i, eGraph, file, function) for i in neighbours)
    iterations = 0
    start_time = int(time.time())

    print(vertices)
    ### how many parallel threads we want
    import os
    n = 16
    tabu_l = []
    best_sol = [initial_solution, results[0][1], results[0][2]]
    neigh = best_sol.copy()
    best_sol, neigh = compare(best_sol, neigh, results)
    neigh = best_sol.copy()
    while not (stoppingCondition(start_time, iterations, max_iteration, timer_stop)):
        iterations = iterations + 1

        neighbours, tabu_l = get_neighbours_alt(tabu_l, neigh[0], neigh_dict, neigh_count, vertices)
        print(str(iterations))
        print(best_sol)
        print(neigh)
        results = []
        results = Parallel(n_jobs=n)(delayed(evalute)(i, eGraph, file, function) for i in neighbours)
        best_sol, neigh = compare(best_sol, neigh, results)
        if len(tabu_l) > maxTabuSize:
            d = len(tabu_l) - maxTabuSize
            del tabu_l[:d]
    print(len(tabu_l))
    return best_sol


def get_neighbours_alt(prev_tabu, current_best, neigh_dict, amount, vertices):
    neighbours_list = []
    iter = 0
    n_test = True
    n_names = list(neigh_dict.keys())
    while len(neighbours_list) < amount / 3 and iter < 40:
        tmp = current_best.copy()
        iter = iter + 1
        for i in range(len(current_best)):
            if tmp[i] == 0:
                neigh = []
                for x in neigh_dict[n_names[i]]:
                    if ("n" + str(x)) in vertices:
                        if current_best[vertices.index("n" + str(x))] == 1:
                            n_test = False
                            break
                        else:
                            n_test = True
                            neigh.append(vertices.index("n" + str(x)))
                if random.randint(0, 10) > 8:
                    if n_test and neigh != []:
                        if random.randint(0, 1):
                            tmp[i] = 1
                        else:
                            pote = random.choice(neigh)
                            if ("n" + str(pote)) in vertices:
                                tmp[vertices.index("n" + str(pote))] = 1
                    else:
                        if random.randint(0, 10) > 5:
                            tmp[i] = 1

        if tmp not in prev_tabu:
            neighbours_list.append(tmp.copy())
            prev_tabu.append(tmp.copy())
    iter = 0
    while len(neighbours_list) < amount * 2 / 3 and iter < 40:
        tmp = current_best.copy()
        iter = iter + 1

        for i in range(len(current_best)):
            if tmp[i] == 1:
                tmp_check = True
                for x in neigh_dict[n_names[i]]:
                    if ("n" + str(x)) in vertices:

                        if current_best[vertices.index("n" + str(x))] == 1:
                            tmp_check = False
                            other = vertices.index("n" + str(x))
                            if random.randint(0, 10) > 7:
                                if random.randint(0, 1):
                                    tmp[i] = 0

                                else:
                                    tmp[other] = 0
                if tmp_check and random.randint(0, 10) > 8:
                    tmp[i] = 0

        if tmp not in prev_tabu:
            neighbours_list.append(tmp.copy())
            prev_tabu.append(tmp.copy())

    iter = 0
    while len(neighbours_list) < amount and iter < 40:
        tmp = current_best.copy()
        iter = iter + 1
        for i in range(len(current_best)):
            if tmp[i] == 1:
                tmp_check = True
                for x in neigh_dict[n_names[i]]:
                    if ("n" + str(x)) in vertices:

                        if current_best[vertices.index("n" + str(x))] == 1:
                            tmp_check = False
                            other = vertices.index("n" + str(x))
                            if random.randint(0, 10) > 7:
                                if random.randint(0, 1):
                                    tmp[i] = 0

                                else:
                                    tmp[other] = 0
                if tmp_check and random.randint(0, 10) > 9:
                    tmp[i] = 0
            else:
                neigh = []
                for x in neigh_dict[n_names[i]]:
                    if ("n" + str(x)) in vertices:
                        if current_best[vertices.index("n" + str(x))] == 1:
                            n_test = False
                            break
                        else:
                            n_test = True
                            neigh.append(vertices.index("n" + str(x)))
                if random.randint(0, 10) > 7:
                    if n_test and neigh != []:
                        if random.randint(0, 1):
                            tmp[i] = 1
                        else:
                            pote = random.choice(neigh)
                            if ("n" + str(pote)) in vertices:
                                tmp[vertices.index("n" + str(pote))] = 1
                    else:
                        if random.randint(0, 10) > 5:
                            tmp[i] = 1
        if tmp not in prev_tabu:
            neighbours_list.append(tmp.copy())
            prev_tabu.append(tmp.copy())

    iter = 0
    while len(neighbours_list) < amount and iter < 40:
        tmp = current_best.copy()
        iter = iter + 1
        for i in range(len(current_best)):

            if random.randint(0, 5) >= 3:
                if tmp[i] == 0:
                    tmp[i] = 1
                else:
                    tmp[i] = 0
        if tmp not in prev_tabu:
            neighbours_list.append(tmp.copy())
            prev_tabu.append(tmp.copy())

    return neighbours_list, prev_tabu


def tabuSearch_alt2(max_iteration, eGraph, file, function, maxTabuSize, timer_stop, neigh_count=16):
    vertices = list(eGraph.get_Potential())
    f = []
    neighbours = []
    neigh_dict = {}
    degree = []
    for n in vertices:
        neigh_dict[n.name] = []

        if n.energyEdgesOut != []:
            for x in list(n.energyEdgesOut):
                neigh_dict[n.name].append(x._Edge__endNode.name)
        if n.energyEdgesIn != []:
            for x in list(n.energyEdgesIn):
                neigh_dict[n.name].append(x._Edge__startNode.name)
        degree.append((n, len(neigh_dict[n.name])))
    for i in range(len(vertices)):
        f.append(1)

    neighbours.append(f)

    results = Parallel(n_jobs=3)(delayed(evalute)(i, eGraph, file, function) for i in neighbours)
    iterations = 0
    start_time = int(time.time())

    print(vertices)
    ### how many parallel threads we want
    import os
    n = 6
    tabu_l = []
    best_sol = [f, results[0][1], results[0][2]]
    neigh = best_sol.copy()
    while not (stoppingCondition(start_time, iterations, max_iteration, timer_stop)):
        iterations = iterations + 1

        neighbours, tabu_l = get_neighbours_alt2(tabu_l, neigh[0], neigh_dict, neigh_count, vertices)
        print(str(iterations))
        print(best_sol)
        print(neigh)
        results = []
        results = Parallel(n_jobs=n)(delayed(evalute)(i, eGraph, file, function) for i in neighbours)
        best_sol, neigh = compare(best_sol, neigh, results)
        if len(tabu_l) > maxTabuSize:
            d = len(tabu_l) - maxTabuSize
            del tabu_l[:d]
    print(len(tabu_l))
    return best_sol

    # frist iteration 19 15 /20 , second 18 17 /20, third added only adding 18 14 18 /20


def get_neighbours_alt2(prev_tabu, current_best, neigh_dict, amount, vertices):
    neighbours_list = []
    iter = 0
    while len(neighbours_list) < 2 / 3 * amount and iter < 4 * amount:
        tmp = current_best.copy()
        iter = iter + 1
        for i in range(len(current_best)):

            if random.randint(0, 20) > 16:
                tmp[i] = 0

        if tmp not in prev_tabu:
            neighbours_list.append(tmp.copy())
            prev_tabu.append(tmp.copy())

    while len(neighbours_list) < amount and iter < 4 * amount:
        tmp = current_best.copy()
        iter = iter + 1
        for i in range(len(current_best)):
            if tmp[i] == 0:
                if random.randint(0, 20) > 18:
                    tmp[i] = 1
        if tmp not in prev_tabu:
            neighbours_list.append(tmp.copy())
            prev_tabu.append(tmp.copy())

    return neighbours_list, prev_tabu
