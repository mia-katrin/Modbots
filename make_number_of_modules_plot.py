import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from mpl_toolkits.mplot3d import Axes3D

from modbots.creature_types.configurable_individual import Individual
from config_util import get_config

config = get_config()

N_INDS = 100000

nr_modules = np.zeros(20)

avg = 0
for _ in range(N_INDS):
    try:
        nrm = Individual.random(config).get_nr_modules()
        nr_modules[nrm] += 1
        avg += nrm
    except:
        pass

avg /= N_INDS
nr_modules /= N_INDS

color = plt.cm.viridis(np.linspace(0, 1, 20))[11]

plt.plot(nr_modules, color=color)
color[-1] = 0.5
plt.fill_between(np.arange(0,20,1), nr_modules, color=color)
plt.xlabel(f"Number of Modules, avg: {avg}")
plt.ylabel("Percentage of population")
plt.xticks([0,3,avg,9,12,15,18], [0,3,avg,9,12,15,18])
plt.title("Average number of modules")
plt.show()
