import json

from modbots.creature_types.string_ind import Individual
from modbots.evaluate import evaluate, set_env_variables, close_env

import argparse
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
set_env_variables(PATH, LOG_FOLDER, seed=SEED, headless=HEADLESS, n_steps=N_STEPS, n_start_eval=N_START_EVAL)
fitness = evaluate(ind)
close_env()

"""liste = node_to_list(ind.bodyRoot)

jsonfile = json.dumps(liste)

with open('jsonfile.json', 'w') as file:
    file.write(jsonfile)

file = open('jsonfile.json', "r")
obj = json.load(file)
print(obj)"""
