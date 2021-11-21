import time

from modbots.evaluate.sideChannelPythonside import SideChannelPythonside
from modbots.evaluate import get_env, evaluate, close_env, set_env_variables
from modbots.creature_types.configurable_individual import Individual

import argparse
import re

from config_util import get_local_config
from localconfig import config

import numpy as np
np.random.seed(42)

# Add arguments
parser = argparse.ArgumentParser(description='Explore some boys')
parser.add_argument(
    '--config_file',
    type = str,
    help='The config file that was used with thiss individual',
    default=get_local_config()
)
parser.add_argument(
    '--gene',
    type = str,
    help='The gene file',
    default="bestInd/ind"
)

args = parser.parse_args()

config.read(args.config_file)

print("We start")
ind = Individual.unpack_ind(args.gene, config)

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
print(f"We got fitness {fitness}")

close_env()
