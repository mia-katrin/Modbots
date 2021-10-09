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

def get_fitnesses(population, time_scale=1.0, no_graphics=False) -> list:
    fitnesses = []

    set_env_variables(seed=42, headless=no_graphics, time_scale=time_scale)

    for ind in population:
        fitnesses.append(
            evaluate(ind)
        )
    close_env()

    return fitnesses

fitnesses_over_all = [[],[]]
times = [[],[]]
for b in [False, True]:
    for time_scale in time_scales_to_test:
        start = time.time()
        fitnesses = get_fitnesses(population, time_scale, no_graphics=b)
        end = time.time()

        times[int(b)].append(end - start) # in seconds
        fitnesses_over_all[int(b)].append(fitnesses)

fig = plt.figure(figsize=(15,15))
fitnesses_over_all = np.array(fitnesses_over_all)

fig.add_subplot(1,3,1)
for i in range(len(fitnesses_over_all[0])):
    plt.plot(fitnesses_over_all[0][i], label=time_scales_to_test[i])
plt.xticks(np.arange(len(population)), [f"Ind {i}" for i in range(len(population))])
plt.xlabel("Individuals")
plt.ylabel("Fitnesses")
plt.legend()

fig.add_subplot(1,3,2)
total_diffs = []
for i in range(1, len(fitnesses_over_all[0])):
    diff = fitnesses_over_all[0][i] - fitnesses_over_all[0][0]
    total_diffs.append(sum(diff))
plt.plot(total_diffs)
plt.xticks(np.arange(len(time_scales_to_test)-1), time_scales_to_test[1:])
plt.xlabel("Time scales tested")
plt.ylabel(f"Total difference from time scale 1 across {len(population)} individuals")

fig.add_subplot(1,3,3)
plt.plot(times[0], label="Graphics")
plt.plot(times[1], label="No graphics", linestyle="dashed")
plt.xticks(np.arange(len(times[0])), time_scales_to_test)
plt.xlabel("Time scales tested")
plt.ylabel("Seconds")
plt.legend()

plt.savefig("results.png")

with open("results.txt", "w") as file:
    file.write("Time used\n")
    file.write("Time scale: Graphics, No Graphics       Diff: G - Not G\n")
    for t0, t1, s in zip(times[0], times[1], time_scales_to_test):
        file.write(f"{s}: {t0}, {t1}       Diff: {t0 - t1}\n")

    file.write("\n\nTotal fitness difference from time scale 1\n")
    file.write("Time scale: Graphics, No Graphics\n")

    total_diffs_noG = []
    for i in range(1, len(fitnesses_over_all[1])):
        diff = fitnesses_over_all[1][i] - fitnesses_over_all[1][0]
        total_diffs_noG.append(sum(diff))

    for d0, d1, s in zip(total_diffs, total_diffs_noG, time_scales_to_test[1:]):
        file.write(f"{s}: {d0}, {d1}\n")

    file.write("\n\nTotal fitness difference from with and without graphics\n")
    file.write("Time scale: Difference\n")

    graphics_diff = []
    for i in range(len(fitnesses_over_all[0])):
        graphics_diff.append(
            sum(fitnesses_over_all[0][i] - fitnesses_over_all[1][i])
        )

    for d, s in zip(graphics_diff, time_scales_to_test):
        file.write(f"{s}: {d}\n")

    file.write("\n\nFitnesses for individuals\n")
    file.write("Time scale: [Ind i with G, Ind i no G] [Ind i+1 with G, Ind i+1 no G]\n")

    for j in range(len(time_scales_to_test)):
        file.write(f"{time_scales_to_test[j]}: ")

        for i in range(NR_INDS):
            file.write(f"[{fitnesses_over_all[0][j][i]}, {fitnesses_over_all[1][j][i]}] ")

        file.write("\n")
