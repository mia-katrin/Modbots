from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.side_channel import (
    SideChannel,
    IncomingMessage,
    OutgoingMessage,
)
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
import numpy as np
import uuid
import os
import matplotlib.pyplot as plt
from tqdm import tqdm
import copy
import multiprocessing
import time

# EA
from deap import base,tools,algorithms

from sideChannelPythonside import SideChannelPythonside

from plotter import Plotter
from individual import Individual
individual_class = Individual

import argparse
from evaluate import get_env, evaluate, close_env, set_env_variables
from evo_util import sort_to_chunks, calc_time_evolution

from IPython import embed

def save_population(population, folder):
    for i, ind in enumerate(population):
        with open(f"{folder}/ind{i}.txt", "w") as file:
            file.write(ind.genome_to_str())
            file.write("\n")
            file.write(str(ind.fitness))
            file.close()

def open_population(run_nr):
    population = []
    cont = True
    i = 0
    while cont:
        try:
            with open(f"experiments/run{run_nr}/population/ind{i}.txt", "r") as file:
                info = file.read().split("\n")
                ind = Individual(info[0])
                ind.fitness = info[1]
                population.append(ind)
                i += 1
        except FileNotFoundError:
            cont = False
            print(f"Run nr {run_nr} ind {i} does not exist, this might be an error, but otherwise we just move on")
    return population

# Not functional yet
def continue_experiment(run_nr):
    population = open_population(run_nr)

    # Set parameters to the same as it was
    with open(f"experiments/run{run_nr}/parameters.txt") as file:
        for line in file.read().split("\n"):
            exec(line)

    last_gen = -1
    cont = True
    while cont:
        try:
            file = open(f"experiments/run{run_nr}/bestInd{last_gen+1}.txt")
            file.close()
            last_gen += 1
        except FileNotFoundError:
            print(f"Last generation was {last_gen-1}. This could be an error")

    # if last_gen == -1, We managed to save population after full init, but got no runs

    start_gen = last_gen + 1

def init_pop(toolbox):
    population = toolbox.population(n=POP_SIZE)

    fitnesses = toolbox.map(toolbox.evaluate, population) # Lazy execution

    for ind, fit in zip(population, fitnesses):
        ind.fitness = fit
        print(f"Fitness: {fit}, Modules: {ind.get_nr_expressed_modules()}")
    return population

def init_toolbox():
    toolbox = base.Toolbox()
    toolbox.register("individual", individual_class.random, depth=IND_DEPTH)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate, force_evaluate=False)
    toolbox.register("mutate", individual_class.mutate, mutation_rate=MUT_RATE)
    toolbox.register("select", tools.selTournament, tournsize = TOURNSIZE)

    if N_CORES > 1:
        print("Starting deap with " , N_CORES , " cores")
        pool = multiprocessing.Pool(N_CORES)
        cs = int(np.ceil(float(POP_SIZE)/float(N_CORES)))
        toolbox.register("map", pool.map, chunksize=cs)
    return toolbox

def evolve():
    assert POP_SIZE%N_CORES == 0, "Cannot run this POP_SIZE because it will cause non-deterministic evaluations"

    print("Generations:", N_GENERATIONS,"\nPopulation:", POP_SIZE,"\nEstimated time:", calc_time_evolution(POP_SIZE, N_CORES, MUT_RATE, NR_PARENTS, N_STEPS, N_GENERATIONS, TIME_SCALE), "seconds")

    if DOCUMENTATION:
        runNr = 0
        with open("experiments/runNr.txt", "r") as file:
            stringNr = file.read()
            runNr = int(stringNr)
        with open("experiments/runNr.txt", "w") as file:
            file.write(f"{runNr + 1}")
            file.close()

        os.makedirs(f"experiments/run{runNr}/")
        os.makedirs(f"experiments/run{runNr}/population/")

        print("What has changed in this run?\n> ", end="")
        if args.statement != None:
            change = args.statement
        else:
            change = input()
        with open(f"experiments/run{runNr}/statement.txt", "w") as file:
            file.write(change)
            file.close()
        with open(f"experiments/all_statements.txt", "a") as file:
            file.write(f"\nRun {runNr}: ")
            file.write(change)
            file.close()

        with open(f"experiments/run{runNr}/parameters.txt", "w") as file:
            file.write("POP_SIZE="+str(POP_SIZE)+"\n")
            file.write("N_GENERATIONS="+str(N_GENERATIONS)+"\n")
            file.write("MUT_RATE="+str(MUT_RATE)+"\n")
            file.write("HEADLESS="+str(HEADLESS)+"\n")
            file.write("N_CORES="+str(N_CORES)+"\n")
            file.write("SEED="+str(SEED)+"\n")
            file.write("IND_DEPTH="+str(IND_DEPTH)+"\n")
            file.write("TOURNSIZE="+str(TOURNSIZE)+"\n")
            file.write("N_STEPS="+str(N_STEPS)+"\n")
            file.write("N_START_EVAL="+str(N_START_EVAL)+"\n")
            file.write("DOCUMENTATION=True\n")
            file.write("TIME_SCALE="+str(TIME_SCALE)+"\n")
            #file.write("PATH="+str(PATH)+"\n")
            file.close()

    set_env_variables(PATH, LOG_FOLDER, seed=SEED, headless=HEADLESS, n_steps=N_STEPS, n_start_eval=N_START_EVAL, time_scale=TIME_SCALE)

    # init toolbox
    toolbox = init_toolbox()

    # Init pop
    population = init_pop(toolbox)

    if DOCUMENTATION:
        save_population(population, folder=f"experiments/run{runNr}/population")

    plotter = Plotter()
    plotter.save_stats(population)
    plotter.print_stats()

    try:
        for gen in tqdm(range(N_GENERATIONS)):
            print("Generation:",gen)

            offspring = toolbox.select(population, POP_SIZE)
            offspring = list(map(toolbox.clone, offspring))

            parents = np.random.choice(offspring, size=NR_PARENTS)
            half = NR_PARENTS//2
            for ind1, ind2 in zip(parents[:half], parents[half:]):
                child1, child2 = ind1.crossover(ind2)
                offspring.append(child2)
                offspring.append(child1)

            for o in offspring:
                o.mutate(MUT_RATE)

            offspring = sort_to_chunks(offspring, nr_chunks=N_CORES)

            fitnesses = toolbox.map(toolbox.evaluate, offspring)
            for ind, fit in zip(offspring, fitnesses):
                ind.fitness = fit

            bestInd = offspring[0]
            for ind in offspring:
                if ind.fitness > bestInd.fitness:
                    bestInd = ind

            population = offspring

            print(f"Best has {bestInd.get_nr_expressed_modules()} modules")

            if DOCUMENTATION:
                with open(f"experiments/run{runNr}/bestInd{gen}.txt", "w") as file:
                    file.write(bestInd.genome_to_str())
                    file.close()

                save_population(population, folder=f"experiments/run{runNr}/population")

            plotter.save_stats(population)
            plotter.print_stats()
    except KeyboardInterrupt:
        close_env()

        inp = input("Do you want to generate plots?")
        if inp != "y":
            raise KeyboardInterrupt("You chose to simply exit")
    close_env()

    print(bestInd.genome_to_str())
    print("Recorded:",bestInd.fitness)

    if DOCUMENTATION:
        plotter.plot_stats(save_figs=True, folder=f"experiments/run{runNr}")
    else:
        plotter.plot_stats()

if __name__ == "__main__":
    # Add arguments
    parser = argparse.ArgumentParser(description='Evolve some boys')
    parser.add_argument(
        'config_file',
        type=str,
        help='The config file to configure this evolution'
    )
    parser.add_argument(
        '-c', '--continue',
        action="store_true",
        help='Wether to continue an evolution or not'
    )
    parser.add_argument(
        '-s', '--statement',
        type=str,
        help="The statement to log."
    )

    args = parser.parse_args()

    # Init config
    with open(args.config_file, "r") as file:
        for line in file:
            exec(line)
            print(line)
    # End of init config

    evolve()
