from math import factorial
import random
from tkinter import N
import numpy
import sys
sys.path.append('./')
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from fitness import fitness_main as ff
from joblib import Parallel, delayed
from load_data import load_netconfig
from graphs.EnergyGraph import EnergyGraph
from fitness import Fitness_modifier as fm


def nsga3_core(iter, eGraph, line_dict_list, fit_obj, div=16):
    vertices = list(eGraph.get_Potential())
    print('GA list of nodes:', vertices)

    # Algorithm parameters
    NOBJ = 3  # number of objectives
    P = div
    H = factorial(NOBJ + P - 1) / (factorial(P) * factorial(NOBJ - 1))
    #MU = int(H + (4 - H % 4))
    MU = div
    NGEN = iter + 1
    CXPB = 1.0
    MUTPB = 0.1
    ##

    # Create uniform reference point
    ref_points = tools.uniform_reference_points(NOBJ, P)

    # Create classes
    creator.create("FitnessMulti", base.Fitness, weights=(1.0, -0.4, 1.0)) #1.0, -1.0, 1.0, 1.0, 1.0 # snr_bottleneck, repeater, data_rateMin_asynchTDMA,
    creator.create("Individual", list, fitness=creator.FitnessMulti)

    # Toolbox Usage
    probability_of_mutation = 0.05
    INDIVIDUAL_SIZE = len(vertices)
    toolbox = base.Toolbox()
    toolbox.register("attr_int", random.randint, 0, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=INDIVIDUAL_SIZE)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    # toolbox.register("evaluate", cg.repeater_evaluate)
    toolbox.register("evaluate", eval_test)
    # toolbox.decorate("evaluate", tools.DeltaPenalty(feasible, 1))
    toolbox.register("mate", tools.cxTwoPoint)  # strategy for crossover, this classic two point crossover
    toolbox.register("mutate", tools.mutFlipBit,
                     indpb=probability_of_mutation)  # mutation strategy with probability of mutation
    toolbox.register("select", tools.selNSGA3, ref_points=ref_points)

    # Start the Process
    # Initialize statistics object
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)

    logbook = tools.Logbook()
    logbook.header = "gen", "evals", "std", "min", "avg", "max"

    pop = toolbox.population(n=MU)
    hall_of_fame = tools.HallOfFame(1)
    pareto = tools.ParetoFront()
    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    t = []
    for i in invalid_ind:
        t.append(list(i))
    import os
    n = 8
    results = []
    """ for i in list(t):
        results.append(evalute(i,eGraph,file,function)) """
    results = Parallel(n_jobs=n)(delayed(evalute)(i, eGraph, line_dict_list, fit_obj) for i in list(t))

    fitnesses = toolbox.map(toolbox.evaluate, results)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # Compile statistics about the population
    record = stats.compile(pop)
    logbook.record(gen=0, evals=len(invalid_ind), **record)
    print(logbook.stream)
    # Dict for final results in Pareto Front
    final_result = {}
    # list with best average snr for each repeater count
    bestlist = []
    # Begin the generational process
    for gen in range(1, NGEN):
        offspring = algorithms.varAnd(pop, toolbox, CXPB, MUTPB)

        # Evaluate the individuals with an invalid fitness

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        ## Needed otherwise not pickable
        t = []
        for i in invalid_ind:
            t.append(list(i))

        results = Parallel(n_jobs=n)(delayed(evalute)(i, eGraph, line_dict_list, fit_obj) for i in list(t))

        fitnesses = toolbox.map(toolbox.evaluate, results)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Select the next generation population from parents and offspring
        pop = toolbox.select(pop + offspring, MU)

        # update list with best average snr for each repeater count
        for individual in results:
            bestIndPerRepeaterCount(individual, bestlist)

        # Compile statistics about the new population
        record = stats.compile(pop)
        logbook.record(gen=gen, evals=len(invalid_ind), **record)
        print(logbook.stream)
        hall_of_fame.update(offspring)
        pareto.update(pop + offspring)
        print('pareto front', pareto)
    best_result = []
    best_fitness = 0
    for best_indi in pareto:
        # using values to return the value and
        repeater_num = best_indi.count(1)
        best_obj_val_overall = best_indi.fitness.values
        final_result.update(
            {"repeater_num": repeater_num, "SNR": best_obj_val_overall[0], "Datarate": best_obj_val_overall[2],
             "individuum": best_indi})
        # print('Minimum value for repeater function: ', best_obj_val_overall)
        print(final_result)
        if best_result == []:
            best_result = final_result.copy()
            best_fitness = best_indi.fitness.values[0] * 1 - 0.4 * best_indi.fitness.values[1]
        else:
            if best_indi.fitness.values[0] * 1 - 0.4 * best_indi.fitness.values[1] > best_fitness:
                best_result = final_result.copy()
                best_fitness = best_indi.fitness.values[0] * 1 - 0.4 * best_indi.fitness.values[1]
        # converting the best solution (snr) into a dict
        '''
        bool_dict = {}
        for i in range(len(best_indi)):
            bool_dict[vertices[i]] = best_indi[i]
        print('The best solution', bool_dict)
        fitness_function_main.final_fitness(best_indi)
        '''

        '''        
            # Plot functions
            plot.plot_graph(int(Tx),net_dict_orig, snr_dict, graph_orig, infeasible_vertices,repeater_list, net_dict_orig, graph)
            vertices_list = [int(a) for a in list(net_dict_orig["bus"].keys()) if a in list(snr_dict.keys())]  # get only connected vertices
            vertices_list.sort()
            plot.plot_SNR_table(int(Tx),graph_orig,snr_dict,repeater_list, infeasible_vertices, vertices_list)
            print (node_tx)
        '''
    return pop, logbook, best_result


def bestIndPerRepeaterCount(individual, bestlist):
    snr, repcount,data = individual
    existing = 0
    if bestlist:
        for i in bestlist:
            if repcount == i[0]:
                existing = 1
                if snr > i[1]:
                    bestlist.remove(i)
                    bestlist.append((repcount, snr))
        if existing == 0:
            bestlist.append((repcount, snr))
    else: bestlist.append((repcount, snr))


"""
def evalute(individual,eGraph,file,function):

    eGraph, line_dict_list  = function(file)
    load_netconfig.auto_generate_netconfig(eGraph)
    EnergyGraph.add_edges(eGraph, line_dict_list)
    SNR_bottleneck,data , total_repeaters =ff.get_fitness_alt(eGraph,individual,file,function)

    return  SNR_bottleneck,total_repeaters,data
"""


def evalute(individual, eGraph, line_dict_list, fit_obj = None):

    if fit_obj is None:
        fit_obj = fm.Fitness_modifier()

    #eGraph, line_dict_list = fit_obj.generate_eGraph()
    fitness_values = fit_obj.calculate_metrics(eGraph, line_dict_list, individual)

    SNR_avg_min = fitness_values['SNR_min']
    SNR_avg_avg = fitness_values['SNR_avg']
    data_rate_min   = fitness_values['data_rate_min']

    return SNR_avg_avg, SNR_avg_min, data_rate_min


def eval_test(indi):
    return indi