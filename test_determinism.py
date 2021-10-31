from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from mlagents_envs.side_channel.side_channel import (
    SideChannel,
    IncomingMessage,
    OutgoingMessage,
)
from mlagents_envs.base_env import ActionTuple

from deap import base,tools,algorithms,creator
import multiprocessing
import numpy as np
import time
import copy

from sideChannelPythonside import SideChannelPythonside
from individual import Individual
from evaluate import get_env, evaluate, close_env, set_env_variables

import argparse
# Add arguments
parser = argparse.ArgumentParser(description='Test determinism on some boys')
parser.add_argument(
    'config_file',
    type=str,
    help='The config file to configure this evolution'
)

with open(parser.parse_args().config_file, "r") as file:
    for line in file:
        exec(line)
        print(line)

NR_INDS = 5
ROUNDS = 5
NR_SEEDS = 2

N_CORES = 2 # It seems this determines a factor in population size
HEADLESS = True

def get_pop(nr_inds:int, duplicates:int = 1, at_least_modules:int = 1, depth:int = 5) -> list:
    pop = []
    for _ in range(nr_inds):
        ind = Individual.random(depth)
        while ind.get_nr_expressed_modules() <at_least_modules:
            ind = Individual.random(depth)
        for _ in range(duplicates):
            pop.append(ind)
    return pop

def test_determinism(fitness_map_function):
    inds = get_pop(NR_INDS, duplicates=ROUNDS, at_least_modules=4)

    all_fitnesses = {}
    for i in range(NR_INDS):
        all_fitnesses[str(i)] = []

    for s in [np.random.randint(100) for _ in range(NR_SEEDS)]:
        print(f"Seed: {s}")

        fitnesses = fitness_map_function(inds, s)

        for i in range(NR_INDS):
            for j in range(ROUNDS):
                all_fitnesses[str(i)].append(fitnesses[i*ROUNDS + j])

    for ind in all_fitnesses:
        print(all_fitnesses[ind])

    for ind in all_fitnesses:
        assert np.all(all_fitnesses[ind] == all_fitnesses[ind][0]), str(all_fitnesses[ind])

def run_sequentially(pop:list, seed:int) -> list:
    # Create the channel
    sc = SideChannelPythonside()

    # We start the communication with the Unity Editor and pass the string_log side channel as input
    set_env_variables(PATH, LOG_FOLDER, seed=seed, headless=HEADLESS)

    fitnesses = []
    for ind in pop:
        fitness = evaluate(ind)
        fitnesses.append(fitness)
        print(f"We got fitness {fitness}")
    close_env()
    return fitnesses

def run_multithreaded(pop:list, seed:int) -> list:
    set_env_variables(PATH, LOG_FOLDER, seed=seed, headless=HEADLESS, time_scale=TIME_SCALE, n_steps=N_STEPS, n_start_eval=N_START_EVAL)

    toolbox = base.Toolbox()
    toolbox.register("evaluate", evaluate)

    # create multiprocessing pool
    pool = multiprocessing.Pool(N_CORES)
    cs = int(np.ceil(float(len(pop)/float(N_CORES))))

    # register the map function in toolbox, toolbox.map can be used to evaluate a population of len(pop)
    toolbox.register("map", pool.map, chunksize=cs)
    deepcopy_pop = copy.deepcopy(pop)
    fitnesses1 = toolbox.map(toolbox.evaluate, pop)
    print(fitnesses1)
    fitnesses2 = toolbox.map(toolbox.evaluate, deepcopy_pop)

    pool.close()
    assert np.all(fitnesses1 == fitnesses2), f"Not all the same\n{fitnesses1}\n{fitnesses2}"

    return fitnesses2

if __name__ == "__main__":
    print(f"This will take above {ROUNDS*NR_INDS*NR_SEEDS*(N_STEPS*0.02)/N_CORES} seconds")
    input()
    start = time.time()
    test_determinism(run_multithreaded)
    print("It took", time.time()-start, "seconds")
