import numpy as np
import os
from tqdm import tqdm
import multiprocessing
import time
from shutil import copyfile
import pickle
from operator import attrgetter

from IPython import embed

# Config
import argparse
from localconfig import config
from config_util import get_local_config

# EA
from deap import base,tools,algorithms

# Modbots
from modbots.plotting.plotter import Plotter
from modbots.creature_types.configurable_individual import Individual
individual_class = Individual
from modbots.evaluate import get_env, evaluate, close_env, set_env_variables#, set_env_seeds
from modbots.util import sort_to_chunks, calc_time_evolution

def get_runNr():
    with open("experiments/runNr.txt", "r") as file:
        nr = file.read()
    return int(nr)

def save_population(population, filename):
    with open(filename, 'wb') as file:
        pickle.dump(population, file)

def open_population(run_nr):
    with open(f"experiments/run{run_nr}/population", 'rb') as file:
        population = pickle.load(file)

    return population

# Not functional
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
            file = open(f"experiments/run{run_nr}/bestInd{last_gen+1}")
            file.close()
            last_gen += 1
        except FileNotFoundError:
            print(f"Last generation was {last_gen-1}. This could be an error")

    # if last_gen == -1, We managed to save population after full init, but got no runs

    start_gen = last_gen + 1

def init_pop(toolbox, config) -> list:
    population = toolbox.population(n=config.ea.pop_size)

    fitnesses = toolbox.map(toolbox.evaluate, population) # Lazy execution

    for ind, fit in zip(population, fitnesses):
        ind.fitness = fit
        print(f"Fitness: {fit}, Modules: {ind.get_nr_modules()}")
    return population

def init_toolbox(config) -> tuple:
    toolbox = base.Toolbox()
    toolbox.register("individual", individual_class.random, config=config)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate, force_evaluate=True)
    toolbox.register("mutate", individual_class.mutate, mutation_rate=config.ea.mut_rate)
    toolbox.register("select", tools.selTournament, tournsize = config.ea.tournsize)

    pool = None
    if config.experiment.n_cores > 1:
        print("Starting deap with ", config.experiment.n_cores, " cores")
        pool = multiprocessing.Pool(config.experiment.n_cores)
        cs = int(np.ceil(float(config.ea.pop_size)/float(config.experiment.n_cores)))
        toolbox.register("map", pool.map, chunksize=cs)
    return toolbox, pool

def print_time(config):
    calc_time = calc_time_evolution(config)
    minutes = calc_time / 60
    hours = minutes / 60
    print(
        "Generations:", config.ea.n_generations,
        "\nPopulation:", config.ea.pop_size,
        "\nEstimated time:", calc_time, "seconds or",
        "\n               ", minutes, "minutes or",
        "\n               ", hours, "hours",
    )

def init_documentation(runNr, statement):
    os.makedirs(f"experiments/run{runNr}/")

    # Save statement
    if statement == None:
        print("What has changed in this run?\n> ", end="")
        statement = input()

    with open(f"experiments/run{runNr}/statement.txt", "w") as file:
        file.write(statement)
    with open(f"experiments/all_statements.txt", "a") as file:
        file.write(f"\nRun {runNr}: {statement}")

    # Save config
    config.save(f"experiments/run{runNr}/{config.filename}")

def evolve(config, statement=None, show_figs=True, runNr=None):
    assert config.ea.pop_size%config.experiment.n_cores == 0, "Cannot run this POP_SIZE because it will cause non-deterministic evaluations"

    print_time(config)

    if config.experiment.documentation:
        if runNr == None:
            runNr = get_runNr()
            with open("experiments/runNr.txt", "w") as file:
                file.write(f"{runNr + 1}")
                file.close()
        init_documentation(runNr, statement)

    set_env_variables(config=config)
    """if 1.0 <= config.evaluation.env_enum <= 2.0:
        set_env_seeds(np.round(np.random.rand(3)*1000))"""

    # init toolbox
    toolbox, pool = init_toolbox(config)

    # Init pop
    population = init_pop(toolbox, config)

    if config.experiment.documentation:
        save_population(population, filename=f"experiments/run{runNr}/population")

    plotter = Plotter()
    plotter.save_stats(population)
    plotter.print_stats()

    try:
        for gen in tqdm(range(config.ea.n_generations)):
            print("Generation:",gen)

            offspring = toolbox.select(population, config.ea.pop_size)
            offspring = list(map(toolbox.clone, offspring))

            # Code graveyard label: Crossover code

            for o in offspring:
                o.mutate(config)

                # Sometimes this method is used for updating things after mutation
                if o.needs_evaluation:
                    o.prepare_for_evaluation()

            # Utilize multithreading as much as possible by forcing heavy jobs into separate chunks
            offspring = sort_to_chunks(offspring, nr_chunks=config.experiment.n_cores)

            fitnesses = toolbox.map(toolbox.evaluate, offspring)

            damaged = False
            for ind, fit in zip(offspring, fitnesses):
                ind.fitness = fit
                if fit == 0.0:
                    damaged = True

            if damaged:
                pool.close()
                pool = multiprocessing.Pool(config.experiment.n_cores)
                cs = int(np.ceil(float(config.ea.pop_size)/float(config.experiment.n_cores)))
                toolbox.register("map", pool.map, chunksize=cs)

                fitnesses = toolbox.map(toolbox.evaluate, offspring)
                for ind, fit in zip(offspring, fitnesses):
                    ind.fitness = fit
                    if fit == 0.0:
                        print("It did not solve the issue of fit=0.0")

            population = offspring

            bestInd = max(population, key=attrgetter('fitness'))
            print(f"Best has {bestInd.get_nr_modules()} modules")

            if config.experiment.documentation:
                bestInd.save_individual(f"experiments/run{runNr}/bestInd{gen}")
                save_population(population, filename=f"experiments/run{runNr}/population")

            plotter.save_stats(population)
            plotter.print_stats()
    except KeyboardInterrupt:
        close_env()
        if config.experiment.n_cores > 1:
            pool.close()

        if input("Do you want to generate plots?") != "y":
            raise KeyboardInterrupt("You chose to simply exit")
    close_env()
    if config.experiment.n_cores > 1:
        pool.close()

    bestInd.save_individual("bestInd/ind")
    print("Recorded:",bestInd.fitness)

    if config.experiment.documentation:
        plotter.plot_stats(save_figs=True, show_figs=show_figs, folder=f"experiments/run{runNr}")
    else:
        if show_figs:
            plotter.plot_stats()

if __name__ == "__main__":
    # Add arguments
    parser = argparse.ArgumentParser(description='Evolve some boys')
    parser.add_argument(
        '--config_file',
        type = str,
        help='The config file to configure this evolution',
        default=get_local_config()
    )
    parser.add_argument(
        '-c', '--continue',
        action="store_true",
        help='Wether to continue an evolution or not'
    )
    parser.add_argument(
        '-s', '--statement',
        type=str,
        help="The statement to log.",
        default=None
    )

    args = parser.parse_args()

    sec = int(np.random.rand()*60)
    print(f"About to sleep {sec} seconds")
    time.sleep(sec)
    print("Woke up")

    config.read(args.config_file)
    config.filename = args.config_file

    evolve(config, statement=args.statement)
