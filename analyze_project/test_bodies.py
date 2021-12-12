from modbots.creature_types.configurable_individual import Individual
from modbots.creature_types.node import Node
from modbots.evaluate import get_env, evaluate, close_env, set_env_variables

from config_util import get_config

import numpy as np
import random
from IPython import embed

config = get_config()

set_env_variables(
    config.files.build_path,
    config.files.log_folder,
    seed=config.experiment.seed,
    headless=config.experiment.headless,
    n_steps=config.evaluation.n_steps,
    n_start_eval=config.evaluation.n_start_eval,
    time_scale=config.evaluation.time_scale
)

ind = Individual.random(config)

for _ in range(20):
    ind.mutate(config)

fitness = evaluate(ind)
print("Fitness", fitness)

close_env()
