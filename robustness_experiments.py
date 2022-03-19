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
from look_at_inds import prune_ind
from morphology_changes import get_morphology_diff
from modbots.evaluate import get_env, evaluate, close_env, set_env_variables
from config_util import get_config_no_args

config_pattern = re.compile("final_?.*\.cfg$")

colors = plt.cm.viridis(np.linspace(0, 1, 4))
transparents = []
colors[-2] = [colors[-2][0]*0.9, colors[-2][1]*0.9, colors[-2][2]*0.9, colors[-2][3]]
colors[-1] = [colors[-1][0]*0.9, colors[-1][1]*0.9, colors[-1][2]*0.9, colors[-1][3]]
for color in colors:
    transparents.append([color[0], color[1], color[2], 0.3])
colors[-1] = [colors[-1][0], colors[-1][1]*0.9, colors[-1][2]*0.9, colors[-1][3]]
#transparents[-2][-1] = 0.35

titles = {
    "sine": "Sine",
    "copy": "Copy CTRNN",
    "dec_ctrnn": "Decentralized CTRNN",
    "cen_ctrnn": "Centralized CTRNN"
}

config = get_config_no_args()
set_env_variables(config=config)

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

def get_config(run_folder):
    for file in os.listdir(run_folder):
        if config_pattern.match(file):
            from localconfig import config
            config.read(f"{run_folder}/{file}")
            config.file_name = file
            return config
    return None

def get_brain_type(config):
    if config.control.oscillatory:
        return "sine"
    elif config.control.ctrnn:
        if config.control.decentral:
            if config.control.copy_decentral:
                return "copy_sine" if config.file_name[:-4].endswith("sine") else "copy"
            return "dec_ctrnn_sine" if config.file_name[:-4].endswith("sine") else "dec_ctrnn"
        return "cen_ctrnn"
    else:
        raise Exception("Failure")

def get_mode(config):
    if config.individual.variable_scale:
        if config.individual.growing:
            if config.individual.gradual:
                return "gradual"
            return "growing"
        return "variable"
    return "normal"

def get_stat(run_folder, data_name="Fitness", stat="Maxs", bestKept=False):
    with open(run_folder+"/data", "rb") as file:
        data = pickle.load(file)
        line = data[data_name][stat]
        if bestKept:
            for i in range(len(line)):
                if i != 0 and line[i-1] > line[i]:
                    line[i] = line[i-1]
        return line

def is_completed_run(run_folder):
    try:
        with open(run_folder + "/data", "rb") as file:
            data = pickle.load(file)
            return True
    except:
        return False

def get_best_ind(run_folder):
    fitnesses = get_stat(run_folder, data_name="Fitness", stat="Maxs", bestKept = True)

    best = fitnesses[-1]
    index = None
    for i in range(len(fitnesses)-1, 0, -1):
        if fitnesses[i] < best:
            break
        index = i - 1

    return Individual.unpack_ind(run_folder + f"/bestInd{index}", get_config(run_folder))

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

        if leaf:
            leaves.append(node)

    return len(leaves) if nr else leaves

def plot_leaves():

    data = []
    labels = []

    with open("runs500_folders.txt", "r") as file:
        folders = file.read().split("\n")[:-1]

    path = "experiments/"

    for folder in folders:
        config = get_config(path + folder)
        brain = get_brain_type(config)
        if brain not in labels:
            labels.append(brain)
            data.append([])

        ind = get_best_ind(path + folder)

        # First get True number of modules
        fitness, counted = evaluate(ind, force_evaluate=True)
        orig_fit = fitness
        orig_count = counted

        # Then get pruned versions
        prune_ind(ind)
        fitness, counted = evaluate(ind, force_evaluate=True)

        if orig_count != counted and orig_fit != fitness:
            print("Diff count:", orig_count, counted, "   Diff fit:", orig_fit, fitness)
        elif orig_count != counted:
            print("Diff count:", orig_count, counted)
        elif orig_fit != fitness:
            print("Diff fitness:", orig_fit, fitness)
        else:
            print("All good")

    close_env()
    #boxplot(data, colors, transparents, labels)

if __name__ == "__main__":
    plot_leaves()
    #plt.show()
