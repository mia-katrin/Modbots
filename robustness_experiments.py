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
import ast

from modbots.creature_types.configurable_individual import Individual
from modbots.creature_types.node import Node
from modbots.plotting.diversity_measure import get_image_of_pop
from modbots.plotting import plot_voxels
from modbots.util import prune_ind, traverse_get_list
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

colors = {
    "copy": colors[0],
    "dec_ctrnn": colors[1],
    "cen_ctrnn": colors[2],
    "sine": colors[3]
}

transparents = {
    "copy": transparents[0],
    "dec_ctrnn": transparents[1],
    "cen_ctrnn": transparents[2],
    "sine": transparents[3]
}

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

def elites_dict(modes = False):
    elites = {}

    filename = "runs500_folders.txt" if not modes else \
               "runs500_folders_modes.txt"

    with open(filename, "r") as file:
        folders = file.read().split("\n")[:-1]

    path = "remote_results/experiments500/"

    for folder in tqdm(folders):
        config = get_config_from_folder(path + folder)
        brain = get_brain_type(config)
        mode = get_mode(config)
        if brain not in elites:
            elites[brain] = [] if not modes else {}
        if modes and mode not in elites[brain]:
            elites[brain][mode] = []

        if modes:
            ind = Individual.unpack_ind(path + folder + "/bestInd499", config)
        else:
            ind = get_best_ind(path + folder)
        prune_ind(ind)

        if modes:
            elites[brain][mode].append((folder, ind))
        else:
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

    plot_diff_dict_sizes(diffs)

def plot_diffs_disable_folder(base_folder):

    elites = elites_dict()
    brains = elites.keys()

    diffs_disable = {}

    for brain in brains:
        diffs_disable[brain] = {0:[], 5:[], 10:[]}

        for i in range(len(elites[brain])):
            folder, ind = elites[brain][i]
            ind.body._nr_expressed_modules = -1
            size = min(10, ind.get_nr_modules() - ind.get_nr_modules()%5)

            path = f"{base_folder}/{folder}"

            with open(path, "r") as file:
                content = file.read().replace("\n", " ")
                fitnesses = ast.literal_eval(content)
                for fit in fitnesses:
                    diffs_disable[brain][size].append((fit, ind.fitness))

    plot_diff_dict_sizes(diffs_disable)

def plot_diff_dict_sizes(diff_dict):
    brains = diff_dict.keys()

    data_percentage = []
    data_full = []
    labels = []
    colors_now = []
    transparents_now = []
    for brain in brains:
        for size in [0,5,10]:
            if (brain == "sine" or brain == "cen_ctrnn") and size == 10:
                continue
            colors_now.append(colors[brain])
            transparents_now.append(transparents[brain])

            up_to = "-" + str(size+5) if size != 10 else "+"
            labels.append(titles[brain] + f" {size}{up_to}")

            values_percentage = []
            values_full = []
            for (disable_fit, ind_fit) in diff_dict[brain][size]:
                values_percentage.append(disable_fit/ind_fit)
                values_full.append(disable_fit)

            data_percentage.append(values_percentage)
            data_full.append(values_full)

    fig = plt.figure()
    fig.add_subplot(2,1,1)
    boxplot(data_full,
        colors_now,
        transparents_now,
        labels)
    plt.xticks([])
    plt.ylabel("Fitness preserved")

    fig.add_subplot(2,1,2)
    boxplot(data_percentage,
        colors_now,
        transparents_now,
        labels)


    plt.yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0], ["0%", "20%", "40%", "60%", "80%", "100%"])
    plt.xticks(rotation = 45)
    plt.ylabel("Fitness preserved")

def disable_and_measure_ind(ind, index):
    def get_actions_new(observation):
        if ind.controller != None:
            actions = ind.controller.get_actions(observation)
            # Dead root
            actions[0][0] = 0.0

            # Dead random
            actions[0][index] = 0.0

            return actions
        return np.zeros((1,50), dtype=float)

    ind.get_actions = get_actions_new

    fitness = evaluate(ind)

    return fitness

def disable_and_measure():
    with open("runs500_folders.txt", "r") as file:
        folders = file.read().split("\n")[:-1]

    path = "experiments/"
    save_path = "diffs_disable/"
    os.makedirs(save_path)

    config = get_config_no_args()
    set_env_variables(config=config)

    for folder in folders:
        fitnesses = []

        ind = get_best_ind(path + folder)
        prune_ind(ind)

        ind.body._nr_expressed_modules = -1
        nr_modules = ind.get_nr_modules()

        for index in range(1, nr_modules):
            ind_on_trial = copy.deepcopy(ind)
            fitness = disable_and_measure_ind(ind_on_trial, index)
            fitnesses.append(fitness)

        with open(save_path + folder, "w") as file:
            file.write(str(fitnesses))

    close_env()

def cut_and_measure_ind(ind, index):
    def traverse_get_list_altered_clone(node, node_list_out):
        node_list_out.append(node)

        for child in node.children:
            if child is not None:
                child.parent = node
                traverse_get_list_altered_clone(child, node_list_out)

    # Get all nodes with parent reference
    all_nodes = []
    traverse_get_list_altered_clone(ind.body.root, all_nodes)

    # Cut away index node
    to_remove = all_nodes[index]
    parent = to_remove.parent
    remove_index = parent.children.index(to_remove)
    parent.children[remove_index] = None

    # Eval
    fitness = evaluate(ind)

    return fitness

def cut_and_measure():
    with open("runs500_folders.txt", "r") as file:
        folders = file.read().split("\n")[:-1]

    path = "experiments/"
    save_path = "diffs_cut/"
    os.makedirs(save_path)

    config = get_config_no_args()
    set_env_variables(config=config)

    for folder in folders:
        fitnesses = []

        ind = get_best_ind(path + folder)
        prune_ind(ind)

        ind.body._nr_expressed_modules = -1
        nr_modules = ind.get_nr_modules()

        for index in range(1, nr_modules):
            ind_on_trial = copy.deepcopy(ind)
            fitness = cut_and_measure_ind(ind_on_trial, index)
            fitnesses.append(fitness)

        with open(save_path + folder, "w") as file:
            file.write(str(fitnesses))

    close_env()

def alter(config, function):
    # [MUTATION]
    config.mutation.control = 0.0
    config.mutation.body = config.mutation.body

    # Body mutation
    config.mutation.angle = 0.0
    config.mutation.copy_branch = 0.0

    function = function.split(" ")
    main = function[0]
    print(function)

    if len(function) > 1:
        mode = function[1]

        config.individual.variable_scale = False
        config.individual.growing = False
        config.individual.gradual = False

        if mode != "normal":
            config.individual.variable_scale = True
            if mode != "variable":
                config.individual.growing = True
                if mode != "growing":
                    config.individual.gradual = True

    if main != "scale":
        config.mutation.scale = 0.0
    elif main == "scale" and not config.individual.variable_scale:
        config.mutation.scale = 0.2
        config.individual.variable_scale = True
    if main != "add":
        config.mutation.add_node = 0.0
    if main != "remove":
        config.mutation.remove_node = 0.0

def apply_and_measure_ind(ind, function, config):
    alter(config, function)

    res = ind.body.mutate_maybe(config)
    while res == None:
        res = ind.body.mutate_maybe(config)

    print(res)

    # Eval
    fitness = evaluate(ind)
    return fitness

def apply_and_measure(save_path, function):
    with open("runs500_folders_modes.txt", "r") as file:
        folders = file.read().split("\n")[:-1]

    path = "experiments/"
    os.makedirs(save_path)

    config = get_config_no_args()
    set_env_variables(config=config)

    for folder in folders:
        fitnesses = []

        config = get_config_from_folder(path + folder)
        ind = Individual.unpack_ind(path + folder + "/bestInd499", config)
        prune_ind(ind)

        ind.body._nr_expressed_modules = -1

        for i in range(5):
            ind_on_trial = copy.deepcopy(ind)
            fitness = apply_and_measure_ind(ind_on_trial, function, config)
            fitnesses.append(fitness)

        with open(save_path + folder, "w") as file:
            file.write(str(fitnesses))

    close_env()

def plot_diffs_modes(base_folder):
    elites = elites_dict(modes=True)
    brains = list(elites.keys())
    modes = elites[brains[0]].keys()

    diffs = {}

    for brain in brains:
        diffs[brain] = {}
        for mode in modes:
            diffs[brain][mode] = []

            for i in range(len(elites[brain][mode])):
                folder, ind = elites[brain][mode][i]
                ind.body._nr_expressed_modules = -1

                path = f"{base_folder}/{folder}"

                with open(path, "r") as file:
                    content = file.read().replace("\n", " ")
                    fitnesses = ast.literal_eval(content)
                    for fit in fitnesses:
                        diffs[brain][mode].append((fit, ind.fitness))

    plot_diff_dict_modes(diffs)

def plot_diff_dict_modes(diff_dict):
    brains = list(diff_dict.keys())
    modes = ["normal", "variable", "growing", "gradual"]

    data_full = []
    labels = []
    colors_now = []
    transparents_now = []
    for brain in brains:
        for mode in modes:
            colors_now.append(colors[brain])
            transparents_now.append(transparents[brain])

            labels.append(titles[brain] + " " +  mode)

            values_full = []
            for (changed_fit, ind_fit) in diff_dict[brain][mode]:
                values_full.append(changed_fit / ind_fit)

            data_full.append(values_full)

    boxplot(data_full,
        colors_now,
        transparents_now,
        labels)
    plt.ylabel("Fitness preserved")
    plt.yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0], ["0%", "20%", "40%", "60%", "80%", "100%"])

    plt.xticks(rotation = 45)
    plt.ylabel("Fitness preserved")

def apply_and_measure_random():
    np.random.seed(0)
    labels = ["add normal", "add variable", "add growing", "add gradual", "remove normal", "remove variable", "remove growing", "remove gradual", "scale"]

    config = get_config_no_args()
    set_env_variables(config=config)

    ROUNDS = 1
    N_INDS = 5
    pop = [Individual.random(config) for _ in range(N_INDS)]

    averages = np.zeros(9)

    for i, ind in enumerate(pop):
        fit = evaluate(ind)

        fitnesses = np.zeros((9,ROUNDS))
        x_axis = []

        for j in range(ROUNDS):
            for k, label in enumerate(labels):
                fitnesses[k,j] = apply_and_measure_ind(
                    copy.deepcopy(ind),
                    label,
                    get_config_no_args()
                ) - fit

            x_axis += list(np.arange(0,9,1)+(1/(2*N_INDS+2))*i)

            label = ("" if j == 0 else "_") + f"Ind {i}"

            plt.bar(np.arange(0,9,1)+(1/(2+ROUNDS+N_INDS))*(i+j), fitnesses[0:9,j], width=1/(N_INDS+2), label=label, color=[i/(N_INDS-1),0.4,(N_INDS-1-i)/(N_INDS-1),0.6])

        averages += np.sum(fitnesses, axis=1) / ROUNDS

    averages /= N_INDS

    for avg, pos in zip(averages, np.arange(0,9,1)):
        x_axis = []
        y_axis = []
        for i in range(2):
            y_axis.append(avg)
            x_axis.append(pos +3/4*i)

        plt.plot(x_axis, y_axis)

    close_env()

    plt.xticks(np.arange(0,9,1), labels)
    plt.xticks(rotation=25)
    plt.legend()
    plt.xlabel("Mutation")
    plt.ylabel("Fitness change")
    plt.title("How mutation affects fitness of random individuals".title())
    plt.show()

if __name__ == "__main__":
    plot_diffs_modes("diffs/diffs_add")
    plt.show()

    #apply_and_measure_random()
