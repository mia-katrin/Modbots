import matplotlib.pyplot as plt
from copy import deepcopy
import numpy as np
import random
import time

from modbots.creature_types.configurable_individual import Individual
from modbots.evaluate import evaluate, set_env_variables, close_env

from evolve import evolve
from config_util import get_config

N_INDS = 5
ROUNDS = 10

def body_mut(name, ind, fitnesses):
    config.mutation.control = 0.0
    config.mutation.body = 1.0

    for var in ["angle", "remove_node", "add_node"]:
        exec(f"config.mutation.{var} = {1.0 if var == name else 0.0}")

    ind_mut = deepcopy(ind)
    ind_mut.mutate(config)
    fitness = evaluate(ind_mut)
    fitnesses[-1] += abs(fitness - ind.fitness)

def cont_mut(ind, fitnesses):
    config.mutation.control = 1.0
    config.mutation.body = 0.0

    ind_mut = deepcopy(ind)
    ind_mut.mutate(config)
    fitness = evaluate(ind_mut)
    fitnesses[-1] += abs(fitness - ind.fitness)

config = get_config()

# Configure config
config.individual.variable_scale = False
config.individual.growing = False

labels = ["angle", "remove_node", "add_node", "control"]

for i in range(N_INDS):
    config.ea.mut_rate = 0.1
    config.mutation.control = 0.5
    config.mutation.body = 0.5

    config.mutation.angle = 0.2
    config.mutation.remove_node = 0.3
    config.mutation.add_node = 0.5

    #evolve(config, show_figs=False)

    #ind = Individual.unpack_ind("bestInd/ind", config)
    ind = Individual.random(config)

    fitnesses = []

    # Get first ind
    #fitness = evaluate(ind)
    #ind.fitness = fitness

    config.ea.mut_rate = 1.0

    set_env_variables(
        config.files.build_path,
        config.files.log_folder,
        seed=config.experiment.seed,
        headless=True,
        n_steps=config.evaluation.n_steps,
        n_start_eval=config.evaluation.n_start_eval,
        time_scale=config.evaluation.time_scale
    )
    fitnesses.append(0)
    for _ in range(ROUNDS):
        body_mut("angle", ind, fitnesses)

    fitnesses.append(0)
    for _ in range(ROUNDS):
        body_mut("remove_node", ind, fitnesses)

    fitnesses.append(0)
    for _ in range(ROUNDS):
        body_mut("add_node", ind, fitnesses)

    fitnesses.append(0)
    for _ in range(ROUNDS):
        cont_mut(ind, fitnesses)

    close_env()

    fitnesses = np.array(fitnesses) / ROUNDS

    plt.bar(np.array([0,1,2,3])+(1/(N_INDS+2))*i, fitnesses, width=1/(N_INDS+2), label=f"Ind {i}")

plt.xticks([0,1,2,3], labels)
plt.legend()
plt.xlabel("Mutation")
plt.ylabel("Fitness change")
plt.title("How mutation affects fitness of random individuals".title())
plt.show()
