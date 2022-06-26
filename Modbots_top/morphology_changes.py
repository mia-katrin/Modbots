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

from modbots.creature_types.configurable_individual import Individual
from look_at_inds import prune_ind

config_pattern = re.compile("final_?.*\.cfg$")

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

def get_nodes_list(body):
    """ Own function to get all body's nodes
    """
    nodes = [body.root]
    index = 0
    while index < len(nodes):
        node = nodes[index]
        index += 1

        for child in node.children:
            if child != None:
                nodes.append(child)

    return nodes

def is_morphology_different(last_ind, ind, only_module_nr=False):
    last_body = last_ind.body
    last_nodes = get_nodes_list(last_body)

    body = ind.body
    nodes = get_nodes_list(body)

    # If they're not equal in length, an addition or removal has happened
    # Otherwise we must check that the nodes are changed
    if len(nodes) == len(last_nodes):
        if only_module_nr:
            return False
        for node1, node2 in zip(last_nodes, nodes):
            if node1.scale != node2.scale or node1.angle != node2.angle or node1.open_spots_list() != node2.open_spots_list():
                return True
        return False
    else:
        return True

def get_morphology_diff(path, only_module_nr=False):
    config = get_config(path)
    diffs = np.zeros(499)
    last_ind = Individual.unpack_ind(path + f"/bestInd0", config)
    prune_ind(last_ind) # Only care about expressed changes
    for i in range(0,499):
        ind = Individual.unpack_ind(path + f"/bestInd{i+1}", config)
        prune_ind(ind) # Only care about expressed changes
        if ind.fitness >= last_ind.fitness:
            changed = is_morphology_different(last_ind, ind, only_module_nr=only_module_nr)
            diffs[i] = int(changed)
            last_ind = ind

    return diffs

if __name__ == "__main__":
    path = "remote_results/experiments500/run13951"

    diffs = get_morphology_diff(path)
    plt.plot(diffs)
    plt.show()
