import os
import matplotlib.pyplot as plt
import numpy as np
import time
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from mlagents_envs.environment import UnityEnvironment

from individual import Individual
from sideChannelPythonside import SideChannelPythonside

from test_determinism import get_pop
from evaluate import evaluate, set_env_variables, close_env

NR_INDS = 5
population = get_pop(nr_inds=NR_INDS, duplicates = 1, at_least_modules = 3, depth = 5)

time_scales_to_test = [1.0, 2.0, 4.0, 10.0, 100.0]
no_graphics = [True]

def get_fitnesses(population, time_scale=1.0, no_graphics=False) -> list:
    fitnesses = []

    set_env_variables(seed=42, headless=no_graphics, time_scale=time_scale)

    for ind in population:
        fitnesses.append(
            evaluate(ind)
        )
    close_env()

    return fitnesses

fitnesses_over_all = [[] for _ in range(len(no_graphics))]
times = [[] for _ in range(len(no_graphics))]
for i, b in enumerate(no_graphics):
    for time_scale in time_scales_to_test:
        start = time.time()
        fitnesses = get_fitnesses(population, time_scale, no_graphics=b)
        end = time.time()

        times[i].append(end - start) # in seconds
        fitnesses_over_all[int(b)].append(fitnesses)

with open("results.txt", "w") as file:
    file.write("Time used\n")

    file.write("\n\nTotal fitness difference from time scale 1\n")
    file.write("Time scale: No Graphics\n")

    total_diffs_noG = []
    for i in range(1, len(fitnesses_over_all[0])):
        diff = fitnesses_over_all[0][i] - fitnesses_over_all[0][0]
        total_diffs_noG.append(sum(diff))

    for d1, s in zip(total_diffs_noG, time_scales_to_test[1:]):
        file.write(f"{s}: {d1}\n")

    file.write("\n\nFitnesses for individuals\n")
    file.write("Time scale: [Ind i with G, Ind i no G]\n")

    for j in range(len(time_scales_to_test)):
        file.write(f"{time_scales_to_test[j]}: ")

        for i in range(NR_INDS):
            file.write(f"[{fitnesses_over_all[0][j][i]}] ")

        file.write("\n")
