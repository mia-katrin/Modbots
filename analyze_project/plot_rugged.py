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
ROUNDS = 5

def body_mut(name, ind):
    config.mutation.control = 0.0
    config.mutation.body = 1.0

    for var in ["angle", "remove_node", "add_node", "scale", "copy_branch"]:
        exec(f"config.mutation.{var} = {1.0 if var == name else 0.0}")

    ind_mut = deepcopy(ind)
    ind_mut.mutate(config)
    fitness = evaluate(ind_mut)
    print(ind_mut.mutation_history)
    return abs(fitness - ind.fitness)

def cont_mut(ind):
    config.mutation.control = 1.0
    config.mutation.body = 0.0

    ind_mut = deepcopy(ind)
    ind_mut.mutate(config)
    fitness = evaluate(ind_mut)
    return abs(fitness - ind.fitness)

config = get_config()

# Configure config
config.individual.variable_scale = True
config.individual.growing = True

labels = ["angle", "remove_node", "add_node", "scale", "copy_branch", "control"]

for i in range(N_INDS):
    config.ea.mut_rate = 0.1
    config.mutation.control = 0.5
    config.mutation.body = 0.5

    config.mutation.angle = 0.1
    config.mutation.remove_node = 0.2
    config.mutation.add_node = 0.3
    config.mutation.scale = 0.2
    config.mutation.copy_branch = 0.2

    set_env_variables(config=config)

    #evolve(config, show_figs=False)

    #ind = Individual.unpack_ind("bestInd/ind", config)
    ind = Individual.random(config)

    # Get first ind
    fitness = evaluate(ind)
    ind.fitness = fitness

    config.ea.mut_rate = 1.0

    fitnesses = np.zeros(6)

    for _ in range(ROUNDS):
        fitnesses[0] += body_mut("angle", ind)

    for _ in range(ROUNDS):
        fitnesses[1] += body_mut("remove_node", ind)

    for _ in range(ROUNDS):
        fitnesses[2] += body_mut("add_node", ind)

    for _ in range(ROUNDS):
        fitnesses[3] += body_mut("scale", ind)

    for _ in range(ROUNDS):
        fitnesses[4] += body_mut("copy_branch", ind)

    for _ in range(ROUNDS):
        fitnesses[5] += cont_mut(ind)

    close_env()

    fitnesses = np.array(fitnesses) / ROUNDS

    plt.bar(np.array([0,1,2,3,4,5])+(1/(N_INDS+2))*i, fitnesses, width=1/(N_INDS+2), label=f"Ind {i}")

plt.xticks([0,1,2,3,4,5], labels)
plt.legend()
plt.xlabel("Mutation")
plt.ylabel("Fitness change")
plt.title("How mutation affects fitness of random individuals".title())
plt.show()
