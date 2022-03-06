import os
import re
import pickle
import numpy as np

from modbots.creature_types.configurable_individual import Individual

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

path = "remote_results/experiments500"

brains = {}

for run_folder in os.listdir(path):
    run_folder = path + "/" + run_folder
    if not os.path.isfile(run_folder):
        config = get_config(run_folder)
        if config == None:
            continue

        data_exists = False
        try:
            with open(run_folder + "/data", "rb") as file:
                data = pickle.load(file)
                data_exists = True
        except:
            pass
        if data_exists:
            continue

        brain = get_brain_type(config)
        if brain == "copy":
            if config.mutation.control == 0.32:
                continue

        last_gen = 0
        for file in os.listdir(run_folder):
            if file.startswith("bestInd"):
                gen = int(file[7:].split(" ")[0])

                if last_gen < gen:
                    last_gen = gen

        if last_gen < 50:
            continue

        print(run_folder + "/bestInd" + str(last_gen))
        ind = Individual.unpack_ind(run_folder + "/bestInd" + str(last_gen-1), config)

        if brain not in brains.keys():
            brains[brain] = [[],[],[]]
        brains[brain][0].append(ind.fitness)
        brains[brain][1].append(last_gen)
        brains[brain][2].append(ind.get_nr_modules())

for brain, (fitnesses, last_gens, modules) in brains.items():
    print(
        brain, ":", np.sum(fitnesses)/len(fitnesses),
        np.sum(last_gens)/len(last_gens),
        len(last_gens),
        np.sum(modules)/len(modules)
    )
