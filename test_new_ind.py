from modbots.evaluate import evaluate, set_env_variables, close_env
from modbots.creature_types.decentralized_sensor_ind import Individual

import argparse
import numpy as np

from modbots.controllers.neural_controller import NeuralController

cont = NeuralController()

# Add arguments
parser = argparse.ArgumentParser(description='Explore some boys')
parser.add_argument(
    'config_file',
    type=str,
    help='The config file to configure this evolution'
)

args = parser.parse_args()
with open(args.config_file, "r") as file:
    for line in file:
        exec(line)
        print(line)

ind = Individual.random(5)
ind2 = Individual(ind.ind_to_str())

set_env_variables(PATH, LOG_FOLDER, seed=SEED, headless=HEADLESS, n_steps=N_STEPS, n_start_eval=N_START_EVAL)

fit1 = evaluate(ind)
fit2 = evaluate(ind2)

print(fit1, fit2)

close_env()
