import json
import matplotlib.pyplot as plt
import numpy as np
from localconfig import config
import colorama
from colorama import Fore, Style
import argparse

from modbots.evaluate import get_env, evaluate, close_env, set_env_variables
from modbots.creature_types.configurable_individual import Individual

# Add arguments
parser = argparse.ArgumentParser(description='Find outliers')
parser.add_argument(
    'label',
    type = str,
    help='The label to check'
)

args = parser.parse_args()

def get_fitness(config, ind):
    set_env_variables(
        config.files.build_path,
        config.files.log_folder,
        seed=config.experiment.seed,
        headless=config.experiment.headless,
        n_steps=config.evaluation.n_steps,
        n_start_eval=config.evaluation.n_start_eval,
        time_scale=config.evaluation.time_scale
    )

    fitness = evaluate(ind)

    close_env()

    return fitness

def check_run(runNr: int, config_file: str):
    print(Fore.WHITE + f"{runNr} report:")
    print(Fore.BLUE + config_file)

    config.read(f"experiments/run{runNr}/{config_file}")
    ind = Individual.unpack_ind(f"experiments/run{runNr}/bestInd{config.ea.n_generations - 1}.txt", config)

    stored_fitness = ind.fitness
    eval_fitness = get_fitness(config, ind)

    if stored_fitness != eval_fitness:
        print(Fore.RED + "Fitness does not correspond")
        print(Fore.RED + "Stored: " + str(stored_fitness))
        print(Fore.RED + "Eval: " + str(eval_fitness))
    else:
        print(Fore.GREEN + "Fitness corresponds")
        print(Fore.GREEN + "Eval: " + str(eval_fitness))
        if eval_fitness > 16:
            print(Fore.CYAN + "Possible outlier")
        elif ind.get_nr_modules() == 1:
            print(Fore.CYAN + "Possible outlier, 1 module")

if __name__ == "__main__":
    with open("experiments/valid_intervals", "r") as file:
        valid_intervals = json.load(file)

    experiment = valid_intervals[args.label]

    for cfg in experiment:
        if not cfg.startswith("Start") and not cfg.startswith("End") and not cfg.startswith("Outliers"):
            for runNr in experiment[cfg]:
                check_run(runNr, cfg)
