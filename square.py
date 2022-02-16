import json
import argparse
import os
import numpy as np
import re
from localconfig import config
from tqdm import tqdm
import pickle
import matplotlib.pyplot as plt

config_pattern = re.compile("[0-9]+c[0-9]+b.*\.cfg$")

class SquareManager:
    def __init__(self):
        """self.squares = {
            "":          {"": Square("remote_experiments/rudolph_experiments"), "variable": Square("remote_experiments/rudolph_experiments"), "growing": Square("remote_experiments/rudolph_experiments"), "gradual": Square("remote_experiments/rudolph_experiments"),},
            "copy":      {"": Square("robinhpc"), "variable": Square("bioint"), "growing": Square("robinhpc"), "gradual": Square("bioint"),},
            "dec_ctrnn": {"": Square("robinhpc"), "variable": Square("bioint"), "growing": Square("bioint"), "gradual": Square("robinhpc"),},
            "cen_ctrnn": {"": Square("robinhpc"), "variable": Square("remote_experiments/rudolph_experiments")},
        }"""
        self.squares = {}

    def get_brain_type(self, config):
        if config.control.oscillatory:
            return ""
        elif config.control.ctrnn:
            if config.control.decentral:
                if config.control.copy_decentral:
                    return "copy"
                return "dec_ctrnn"
            return "cen_ctrnn"
        else:
            raise Exception("Failure")

    def get_mode(self, config):
        if config.individual.variable_scale:
            if config.individual.growing:
                if config.individual.gradual:
                    return "gradual"
                return "growing"
            return "variable"
        return ""

    def get_config(self, run_folder):
        for file in os.listdir(run_folder):
            if config_pattern.match(file):
                config.read(f"{run_folder}/{file}")
                return config
        return None

    def add_run(self, run_folder) -> bool:
        runNr = int(run_folder.split("/")[-1][3:])

        cfg = self.get_config(run_folder)
        if cfg is None:
            return False

        mode = self.get_mode(config)
        brain_type = self.get_brain_type(config)

        if brain_type not in self.squares.keys():
            self.squares[brain_type] = {}
        if mode not in self.squares[brain_type].keys():
            exp_folder = "/".join(run_folder.split("/")[:-1])
            self.squares[brain_type][mode] = Square(exp_folder)

        self.squares[brain_type][mode].add_run(
            runNr,
            config.mutation.control,
            config.mutation.body
        )
        return True

    def print_all(self):
        print()
        for brain_type in self.squares.keys():
            for mode in self.squares[brain_type].keys():
                print(brain_type.title() if brain_type != "" else "Sine", mode.title(),"\n")
                self.squares[brain_type][mode].print_nr_runs()

    def plot_all(self):
        full_matrix = np.zeros((8*4,8*4))
        for i, brain_type in enumerate(self.squares.keys()):
            for j, mode in enumerate(self.squares[brain_type].keys()):
                matrix, cs, bs = self.squares[brain_type][mode].get_fitness_matrix()
                full_matrix[i*8:i*8+len(cs),j*8:j*8+len(bs)] = matrix

        fig1, ax1 = plt.subplots(1, sharex = True, sharey = False)
        ax1.imshow(full_matrix.astype(int))
        for i, row in enumerate(full_matrix):
            for j, val in enumerate(row):
                if val != 0:
                    ax1.text(j, i, round(val), color='black', ha='center', va='center')

        plt.show()

class Square:
    def __init__(self, experiment_folder: str):
        self.experiment_folder = experiment_folder
        self.runs = {}

        self.print_filled = self.treat_spots(self.internal_fill_spot)
        self.print_fitnesses = self.treat_spots(self.internal_fitness_spot)
        self.print_nr_runs = self.treat_spots(self.internal_count_runs_fill)
        self.print_avg_mutated = self.treat_spots(self.internal_avg_mutated_spot)

        self.get_fitness_matrix = self.get_matrix_getter(self.get_fitness)

    def add_run(self, runNr, c, b):
        if c not in self.runs.keys():
            self.runs[c] = {}

        if b not in self.runs[c].keys():
            self.runs[c][b] = []

        self.runs[c][b].append(runNr)

    def get_cs(self):
        cs = []
        for c in self.runs.keys():
            cs.append(c)

        return sorted(list(set(cs)), reverse=True)

    def get_bs(self):
        bs = []
        for c in self.runs.keys():
            for b in self.runs[c].keys():
                bs.append(b)

        return sorted(list(set(bs)))

    def get_fitness(self, c, b):
        average = 0
        valid_runs = 0
        for runNr in self.runs[c][b]:
            path = f"{self.experiment_folder}/run{runNr}"
            try:
                with open(path+"/data", "rb") as file:
                    data = pickle.load(file)
                    average += data["Fitness"]["Maxs"][-1]
                    valid_runs += 1
            except:
                pass

        return 0 if valid_runs == 0 else average / valid_runs

    def get_avg_mutated(self, c, b):
        average = 0
        valid_runs = 0
        for runNr in self.runs[c][b]:
            path = f"{self.experiment_folder}/run{runNr}"
            try:
                with open(path+"/data", "rb") as file:
                    data = pickle.load(file)
                    average = max(average, np.sum(data["Nr Mutated"])/51)
                    valid_runs += 1
            except:
                pass

        return 0 if valid_runs == 0 else average

    def get_valid_runs(self, c, b):
        valid_runs = 0
        for runNr in self.runs[c][b]:
            path = f"{self.experiment_folder}/run{runNr}"
            try:
                with open(path+"/data", "rb") as file:
                    data = pickle.load(file)
                    valid_runs += 1
            except:
                pass
        return valid_runs

    def internal_fill_spot(self, c, b, width):
        if b in self.runs[c].keys():
            return "".center(width, "█")
        else:
            return "".center(width, " ")

    def internal_fitness_spot(self, c, b, width):
        if b in self.runs[c].keys():
            fitness = round(self.get_fitness(c,b), 2)
            return str(fitness).ljust(width, " ")
        else:
            return "".center(width, " ")

    def internal_count_runs_fill(self, c, b, width):
        if b in self.runs[c].keys():
            nr_runs = self.get_valid_runs(c,b)
            return str(nr_runs).center(width, " ")
        else:
            return "".center(width, " ")

    def internal_avg_mutated_spot(self, c, b, width):
        if b in self.runs[c].keys():
            avg_mutated = round(self.get_avg_mutated(c,b), 2)
            return str(avg_mutated).ljust(width, " ")
        else:
            return "".center(width, " ")

    def treat_spots(self, function):
        def internal():
            width = 6

            bs = self.get_bs()

            bline = "      "
            overline = "     |"
            for b in bs:
                bline += str(b).ljust(width)
                overline += "".center(width, "_")
            bline += "\n"
            overline += "\n"

            cs = self.get_cs()
            cline = ""
            for c in cs:
                cline += str(c).ljust(4) + " |"

                for b in bs:
                    cline += function(c,b,width)

                cline += "\n"

            print(cline + overline + bline)
        return internal

    def get_matrix_getter(self, function):
        def internal():
            bs = self.get_bs()
            cs = self.get_cs()

            matrix = np.zeros((len(cs),len(bs)))

            for i, c in enumerate(cs):
                for j, b in enumerate(bs):
                    if b in self.runs[c].keys():
                        matrix[i,j] = function(c,b)

            return matrix, cs, bs
        return internal
