"""
A file for exploring individuals, specifying configs, ind files, or random inds.
"""
from modbots.evaluate.sideChannelPythonside import SideChannelPythonside
from modbots.evaluate import get_env, evaluate, close_env, set_env_variables
from modbots.creature_types.configurable_individual import Individual

import argparse

from config_util import get_local_config
from localconfig import config

# Add arguments
parser = argparse.ArgumentParser(description='Explore some boys')
parser.add_argument(
    '--config_file',
    type = str,
    help='The config file that was used with this individual',
    default=get_local_config()
)
parser.add_argument(
    '--gene',
    type = str,
    help='The gene file. Write "random" to get a random ind using the config',
    default="bestInd/ind"
)
parser.add_argument(
    '--record',
    action="store_true",
    help='To record or not. Recording saved in recorded_ind.txt, and can be played with play.py',
    default=False
)

# Rad arguments
args = parser.parse_args()

# Get the config to use
config.read(args.config_file)

# Get individual
if args.gene == "random":
    ind = Individual.random(config)
    print("Starting random ind")
else:
    ind = Individual.unpack_ind(args.gene, config)
    print("Stored fitness:", ind.fitness)

# Evaluate
set_env_variables(config=config)

fitness = evaluate(ind, force_evaluate=True, record=args.record)
print(f"We got fitness {fitness}")

close_env()

"""if args.gene != "random":
    print("\nMutation history:")
    print(ind.mutation_history)"""
