""" Script for finding individuals that don't have the same fitness as their
recorded fitness. Also to find small and too good individuals.
Not very important, just used for debugging. """

import json
import matplotlib.pyplot as plt
import numpy as np
from localconfig import config
import colorama
from colorama import Fore, Style
import argparse

from modbots.evaluate import get_env, evaluate, close_env, set_env_variables
from modbots.creature_types.configurable_individual import Individual

def get_fitness(config, ind):
    set_env_variables(config=config)

    fitness = evaluate(ind)

    close_env()

    return fitness

def check_run(runNr: int, config_file: str):
    print(Fore.WHITE + f"{runNr} report:")
    print(Fore.BLUE + config_file)

    config.read(f"experiments/run{runNr}/{config_file}")
    ind = Individual.unpack_ind(f"experiments/run{runNr}/bestInd{config.ea.n_generations - 1}", config)

    stored_fitness = ind.fitness
    eval_fitness = get_fitness(config, ind)

    if stored_fitness != eval_fitness:
        print(Fore.RED + "Fitness does not correspond")
        print(Fore.RED + "Stored: " + str(stored_fitness))
        print(Fore.RED + "Eval: " + str(eval_fitness))
        return False
    else:
        print(Fore.GREEN + "Fitness corresponds")
        print(Fore.GREEN + "Eval: " + str(eval_fitness))
        if eval_fitness > 16:
            print(Fore.CYAN + "Possible outlier")
        if ind.get_nr_modules() <= 2:
            print(Fore.CYAN + f"Possible outlier, {ind.get_nr_modules()} module")
    return True

if __name__ == "__main__":
    # Add arguments
    parser = argparse.ArgumentParser(description='Find outliers')
    parser.add_argument(
        'label',
        type = str,
        help='The label to check'
    )

    args = parser.parse_args()

    with open("experiments/valid_intervals", "r") as file:
        valid_intervals = json.load(file)

    for label in valid_intervals.keys():
        if label.startswith(args.label):
            print(Fore.WHITE + label)
            print()
            experiment = valid_intervals[label]

            for cfg in experiment:
                if not cfg.startswith("Start") and not cfg.startswith("End") and not cfg.startswith("Outliers"):
                    broken = False
                    for runNr in experiment[cfg]:
                        try:
                            all_good = check_run(runNr, cfg)
                            if not all_good:
                                print("This run is busted. I recommend deletion")
                                broken = True
                                break
                        except:
                            print(f"Run {runNr} is not fine")
                    if broken:
                        break

    print(Fore.WHITE + "Goodbye")
