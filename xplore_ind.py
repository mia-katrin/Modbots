import time

from modbots.evaluate.sideChannelPythonside import SideChannelPythonside
from modbots.evaluate import get_env, evaluate, close_env, set_env_variables
from modbots.creature_types.string_ind import Individual

import argparse
import re

def get_type(gene):
    float_pat = rf""
    pattern = rf"()"

# Add arguments
parser = argparse.ArgumentParser(description='Explore some boys')
parser.add_argument(
    'config_file',
    type=str,
    help='The config file to configure this evolution'
)
parser.add_argument(
    'gene',
    type=str,
    help='The gene to evaluate'
)

args = parser.parse_args()
with open(args.config_file, "r") as file:
    for line in file:
        exec(line)
        print(line)

ind_type = get_type(args.gene)

print("We start")
start = time.time()
ind = Individual(args.gene)
set_env_variables(PATH, LOG_FOLDER, seed=SEED, headless=HEADLESS, n_steps=N_STEPS, n_start_eval=N_START_EVAL)
print("Starting:", time.time()-start)

start = time.time()
fitness = evaluate(ind)
print("Evaluating:", time.time()-start)
print(f"We got fitness {fitness}")

start = time.time()
close_env()
print("Closing:", time.time()-start)
