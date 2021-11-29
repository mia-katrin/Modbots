import numpy as np
import os
from tqdm import tqdm
import multiprocessing
import time
from shutil import copyfile
import pickle

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
from modbots.evaluate import get_env, evaluate, close_env, set_env_variables
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
            file = open(f"experiments/run{run_nr}/bestInd{last_gen+1}.txt")
            file.close()
            last_gen += 1
        except FileNotFoundError:
            print(f"Last generation was {last_gen-1}. This could be an error")

    # if last_gen == -1, We managed to save population after full init, but got no runs

    start_gen = last_gen + 1

def init_pop(toolbox, config):
    population = toolbox.population(n=config.ea.pop_size)

    fitnesses = toolbox.map(toolbox.evaluate, population) # Lazy execution

    for ind, fit in zip(population, fitnesses):
        ind.fitness = fit
        print(f"Fitness: {fit}, Modules: {ind.get_nr_modules()}")
    return population

def init_toolbox(config):
    toolbox = base.Toolbox()
    toolbox.register("individual", individual_class.random, config=config)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate, force_evaluate=False)
    toolbox.register("mutate", individual_class.mutate, mutation_rate=config.ea.mut_rate)
    toolbox.register("select", tools.selTournament, tournsize = config.ea.tournsize)

    pool = None
    if config.experiment.n_cores > 1:
        print("Starting deap with ", config.experiment.n_cores, " cores")
        pool = multiprocessing.Pool(config.experiment.n_cores)
        cs = int(np.ceil(float(config.ea.pop_size)/float(config.experiment.n_cores)))
        toolbox.register("map", pool.map, chunksize=cs)
    return toolbox, pool

def evolve(config, statement=None, show_figs=True):
    assert config.ea.pop_size%config.experiment.n_cores == 0, "Cannot run this POP_SIZE because it will cause non-deterministic evaluations"

    calc_time = calc_time_evolution(config.ea.pop_size, config.experiment.n_cores, config.ea.mut_rate, config.ea.nr_parents, config.evaluation.n_steps, config.ea.n_generations, config.evaluation.time_scale)
    minutes = calc_time / 60
    hours = minutes / 60
    print(
        "Generations:", config.ea.n_generations,
        "\nPopulation:", config.ea.pop_size,
        "\nEstimated time:", calc_time, "seconds or",
        "\n               ", minutes, "minutes or",
        "\n               ", hours, "hours",
    )

    if config.experiment.documentation:
        runNr = get_runNr()
        with open("experiments/runNr.txt", "w") as file:
            file.write(f"{runNr + 1}")
            file.close()

        os.makedirs(f"experiments/run{runNr}/")

        # Save statement
        if statement != None:
            change = statement
        elif args.statement != None:
            change = args.statement
        else:
            print("What has changed in this run?\n> ", end="")
            change = input()
        with open(f"experiments/run{runNr}/statement.txt", "w") as file:
            file.write(change)
        with open(f"experiments/all_statements.txt", "a") as file:
            file.write(f"\nRun {runNr}: {change}")

        # Save config
        config.save(f"experiments/run{runNr}/{config.filename}")

    set_env_variables(
        config.files.build_path,
        config.files.log_folder,
        seed=config.experiment.seed,
        headless=config.experiment.headless,
        n_steps=config.evaluation.n_steps,
        n_start_eval=config.evaluation.n_start_eval,
        time_scale=config.evaluation.time_scale
    )

    # init toolbox
    toolbox, pool = init_toolbox(config)

    # Init pop
    population = init_pop(toolbox, config)

    if config.experiment.documentation:
        save_population(population, filename=f"experiments/run{runNr}/population")

    plotter = Plotter()
    plotter.save_stats(population)
    plotter.print_stats()

    bestInd = population[0]
    for ind in population:
        if ind.fitness > bestInd.fitness:
            bestInd = ind

    try:
        for gen in tqdm(range(config.ea.n_generations)):
            print("Generation:",gen)

            offspring = toolbox.select(population, config.ea.pop_size-1)
            offspring = list(map(toolbox.clone, offspring))
            offspring.append(toolbox.clone(bestInd))

            """parents = np.random.choice(offspring, size=config.ea.nr_parents)
            half = config.ea.nr_parents//2
            for ind1, ind2 in zip(parents[:half], parents[half:]):
                child1, child2 = ind1.crossover(ind2)
                offspring.append(child2)
                offspring.append(child1)"""

            for o in offspring:
                o.mutate(config)

                if o.needs_evaluation:
                    o.prepare_for_evaluation()

            # Utilize multithreading as much as possible by forcing heavy jobs
            # into separate chunks
            offspring = sort_to_chunks(offspring, nr_chunks=config.experiment.n_cores)

            fitnesses = toolbox.map(toolbox.evaluate, offspring)
            for ind, fit in zip(offspring, fitnesses):
                ind.fitness = fit

            for ind in offspring:
                if ind.fitness > bestInd.fitness:
                    bestInd = ind

            population = offspring

            print(f"Best has {bestInd.get_nr_modules()} modules")

            if config.experiment.documentation:
                bestInd.save_individual(f"experiments/run{runNr}/bestInd{gen}.txt")
                save_population(population, filename=f"experiments/run{runNr}/population")

            plotter.save_stats(population)
            plotter.print_stats()
    except KeyboardInterrupt:
        close_env()
        pool.close()

        inp = input("Do you want to generate plots?")
        if inp != "y":
            raise KeyboardInterrupt("You chose to simply exit")
    close_env()
    pool.close()

    bestInd.save_individual("bestInd/ind")
    print("Recorded:",bestInd.fitness)

    if config.experiment.documentation:
        plotter.plot_stats(save_figs=True, show_figs=show_figs, folder=f"experiments/run{runNr}")
    else:
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
        help="The statement to log."
    )

    args = parser.parse_args()

    config.read(args.config_file)
    config.filename = args.config_file

    evolve(config)
