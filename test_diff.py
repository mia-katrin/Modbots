import time

from modbots.evaluate.sideChannelPythonside import SideChannelPythonside
from modbots.evaluate import get_env, evaluate, close_env, set_env_variables
from modbots.creature_types.configurable_individual import Individual

import argparse
import re

from config_util import get_local_config, get_config
from localconfig import config

import numpy as np
import random

config = get_config()

print("We start")
np.random.seed(42)
random.seed(42)
ind = Individual.random(config)

from modbots.util import traverse_get_list
allNodes = []
traverse_get_list(ind.body.root, allNodes)

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
fitness = evaluate(ind)
print(f"We got fitness {fitness}")

close_env()
