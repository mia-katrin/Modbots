import json
import argparse
import os
import numpy as np
import re
from tqdm import tqdm
import pickle
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import pandas as pd
import scipy.stats as stats
import copy
import pandas as pd
import seaborn as sns
import os
import matplotlib.pyplot as plt
import matplotlib.collections as clt
import ptitprince as pt

from modbots.creature_types.configurable_individual import Individual
from modbots.plotting.diversity_measure import get_image_of_pop
from modbots.plotting import plot_voxels
from modbots.util import prune_ind
from morphology_changes import get_morphology_diff
from modbots.evaluate import get_env, evaluate, close_env, set_env_variables
from config_util import get_config_no_args, get_config_from_folder, get_mode, get_brain_type

colors = plt.cm.viridis(np.linspace(0, 1, 4))
transparents = []
colors[-2] = [colors[-2][0]*0.9, colors[-2][1]*0.9, colors[-2][2]*0.9, colors[-2][3]]
colors[-1] = [colors[-1][0]*0.9, colors[-1][1]*0.9, colors[-1][2]*0.9, colors[-1][3]]
for color in colors:
    transparents.append([color[0], color[1], color[2], 0.3])
colors[-1] = [colors[-1][0], colors[-1][1]*0.9, colors[-1][2]*0.9, colors[-1][3]]
#transparents[-2][-1] = 0.35

titles = {
    "copy": "Copy",
    "dec_ctrnn": "Dec.",
    "cen_ctrnn": "Cen.",
    "sine": "Sine"
}

def boxplot(data, edge_color, fill_color, labels):
    bp = plt.boxplot(data, patch_artist=True, showmeans=True, labels=labels)

    for i, patch in enumerate(bp['boxes']):
        patch.set(color=edge_color[i])
    for i, patch in enumerate(bp['boxes']):
        patch.set(facecolor=fill_color[i])

    for i, patch in enumerate(bp['medians']):
        patch.set(color=edge_color[i])

    for i, patch in enumerate(bp['caps']):
        patch.set(color=edge_color[i//2])
    for i, patch in enumerate(bp['whiskers']):
        patch.set(color=edge_color[i//2])
    for i, patch in enumerate(bp['fliers']):
        patch.set(color=edge_color[i])

    return bp

def get_stat(run_folder, data_name="Fitness", stat="Maxs", bestKept=False):
    with open(run_folder+"/data", "rb") as file:
        data = pickle.load(file)
        line = data[data_name][stat]
        if bestKept:
            for i in range(len(line)):
                if i != 0 and line[i-1] > line[i]:
                    line[i] = line[i-1]
        return line

def get_best_ind(run_folder):
    fitnesses = get_stat(run_folder, data_name="Fitness", stat="Maxs", bestKept = True)

    best = fitnesses[-1]
    index = None
    for i in range(len(fitnesses)-1, 0, -1):
        if fitnesses[i] < best:
            break
        index = i - 1

    return Individual.unpack_ind(run_folder + f"/bestInd{index}", get_config_from_folder(run_folder))

def get_leaves(ind, nr = False):
    leaves = []

    stack = [ind.body.root]

    while len(stack) > 0:
        node = stack.pop(0)

        leaf = True
        for child in node.children:
            if not child is None:
                leaf = False
                stack.append(child)
                child.parent = node

        if leaf:
            leaves.append(node)

    return len(leaves) if nr else leaves

def elites_dict():
    elites = {}

    with open("runs500_folders.txt", "r") as file:
        folders = file.read().split("\n")[:-1]

    path = "remote_results/experiments500/"

    for folder in tqdm(folders):
        config = get_config_from_folder(path + folder)
        brain = get_brain_type(config)
        if brain not in elites:
            elites[brain] = []

        ind = get_best_ind(path + folder)
        prune_ind(ind)
        elites[brain].append((folder, ind))

    return elites

def plot_diffs_folder(base_folder):

    elites = elites_dict()
    brains = elites.keys()

    diffs = {}

    for brain in brains:
        diffs[brain] = {0:[], 5:[], 10:[]}

        for i in range(len(elites[brain])):
            folder, ind = elites[brain][i]
            ind.body._nr_expressed_modules = -1
            size = min(10, ind.get_nr_modules() - ind.get_nr_modules()%5)

            path = f"{base_folder}/{folder}"

            for file_ind in os.listdir(path):
                with open(path + "/" + file_ind, "rb") as file:
                    leaf_ind = pickle.load(file)

                    diffs[brain][size].append((leaf_ind.fitness, ind.fitness))

    data = []
    labels = []
    for brain in brains:
        for size in [0,5,10]:
            up_to = "-" + str(size+5) if size != 10 else "+"
            labels.append(titles[brain] + f" {size}{up_to}")

            values = []
            for (leaf_fit, ind_fit) in diffs[brain][size]:
                values.append(leaf_fit/ind_fit)
            data.append(values)

    boxplot(data,
        np.concatenate([[colors[i] for _ in range(3)] for i in range(4)]),
        np.concatenate([[transparents[i] for _ in range(3)] for i in range(4)]),
        labels)

    plt.yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0], ["0%", "20%", "40%", "60%", "80%", "100%"])
    plt.xticks(rotation = 45)
    plt.ylabel("Fitness preserved")

def disable_and_measure_ind(ind):
    ind = copy.deepcopy(ind)

    ind.disable_number = np.random.rand()

    def get_actions_new(observation):
        if ind.controller != None:
            actions = ind.controller.get_actions(observation)
            # Dead root
            actions[0][0] = 0.0

            # Dead random
            index = 1 + ind.disable_number * (len(actions[0])-2)
            index = int(round(index))
            actions[0][index] = 0.0

            return actions
        return np.zeros((1,50), dtype=float)

    ind.get_actions = get_actions_new

    fitness = evaluate(ind)

    print(ind.fitness, fitness)

    return fitness

def disable_and_measure():
    with open("runs500_folders.txt", "r") as file:
        folders = file.read().split("\n")[:-1]

    path = "experiments/"

    config = get_config_no_args()
    set_env_variables(config=config)

    for folder in folders:
        ind = get_best_ind(path + folder)
        prune_ind(ind)
        fitness = disable_and_measure_ind(ind)

    close_env()

if __name__ == "__main__":
    #plot_diffs_folder("diffs")
    #plt.show()
    disable_and_measure()
