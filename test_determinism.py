from deap import base,tools,algorithms,creator
import multiprocessing
import numpy as np
import time
import copy

from IPython import embed

from modbots.evaluate.sideChannelPythonside import SideChannelPythonside
from modbots.creature_types.configurable_individual import Individual
from modbots.evaluate import get_env, evaluate, close_env, set_env_variables

from config_util import get_config

NR_INDS = 25
ROUNDS = 5
NR_SEEDS = 5

N_CORES = 25 # It seems this determines a factor in population size
HEADLESS = True
TIME_SCALE = None

def get_pop(nr_inds:int, config, duplicates:int = 1, at_least_modules:int = 1) -> list:
    pop = []
    for _ in range(nr_inds):
        ind = Individual.random(config)
        while ind.get_nr_modules() < at_least_modules:
            ind = Individual.random(config)
        for _ in range(duplicates):
            pop.append(ind)
    return pop

def test_determinism(fitness_map_function, config):
    inds = get_pop(NR_INDS, config, duplicates=ROUNDS, at_least_modules=4)

    all_fitnesses = {}
    for i in range(0, NR_INDS):
        inds[i*ROUNDS].index = i
        all_fitnesses[str(i)] = []

    for s in [np.random.randint(100) for _ in range(NR_SEEDS)]:
        print(f"Seed: {s}")

        np.random.shuffle(inds)
        fitnesses = fitness_map_function(inds, s, config)

        for fit, ind in zip(fitnesses, inds):
            all_fitnesses[str(ind.index)].append(fit)

    for ind in all_fitnesses:
        print(all_fitnesses[ind])

    for ind in all_fitnesses:
        assert np.all(all_fitnesses[ind] == all_fitnesses[ind][0]), str(all_fitnesses[ind])

def run_sequentially(pop:list, seed:int, config) -> list:
    # Create the channel
    sc = SideChannelPythonside()

    # We start the communication with the Unity Editor and pass the string_log side channel as input
    set_env_variables(config=config, seed=seed, headless=HEADLESS, time_scale=TIME_SCALE)

    fitnesses = []
    for ind in pop:
        fitness = evaluate(ind)
        fitnesses.append(fitness)
        print(f"We got fitness {fitness}")
    close_env()
    return fitnesses

def run_multithreaded(pop:list, seed:int, config) -> list:
    set_env_variables(config=config, seed=seed, headless=HEADLESS, time_scale=TIME_SCALE)

    toolbox = base.Toolbox()
    toolbox.register("evaluate", evaluate)

    # create multiprocessing pool
    pool = multiprocessing.Pool(N_CORES)
    cs = int(np.ceil(float(len(pop)/float(N_CORES))))

    # register the map function in toolbox, toolbox.map can be used to evaluate a population of len(pop)
    toolbox.register("map", pool.map, chunksize=cs)
    #deepcopy_pop = copy.deepcopy(pop)
    fitnesses1 = toolbox.map(toolbox.evaluate, pop)
    print(fitnesses1)
    #fitnesses2 = toolbox.map(toolbox.evaluate, deepcopy_pop)

    pool.close()
    #assert np.all(fitnesses1 == fitnesses2), f"Not all the same\n{fitnesses1}\n{fitnesses2}"

    return fitnesses1

if __name__ == "__main__":
    config = get_config()

    print(f"This will take above {ROUNDS*NR_INDS*NR_SEEDS*(config.evaluation.n_steps*0.2)/N_CORES} seconds")
    #input()
    start = time.time()
    test_determinism(run_multithreaded, config)
    print("It took", time.time()-start, "seconds")
