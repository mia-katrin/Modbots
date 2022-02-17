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

def boxplot(data, edge_color, fill_color, labels, ax):
    bp = ax.boxplot(data, patch_artist=True, showmeans=True, labels=labels)

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

    def print_all(self, runs=False):
        print()
        for brain_type in self.squares.keys():
            for mode in self.squares[brain_type].keys():
                print(brain_type.title() if brain_type != "" else "Sine", mode.title(),"\n")
                if runs:
                    self.squares[brain_type][mode].print_nr_runs()
                else:
                    self.squares[brain_type][mode].print_fitnesses()

    def plot_all(self, runs=False):
        for i, brain_type in enumerate(self.squares.keys()):
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex = True, sharey = False)
            fig.suptitle(brain_type.title())

            subplot_axes = (ax1, ax2, ax3, ax4)

            for j, mode in enumerate(self.squares[brain_type].keys()):
                ax = subplot_axes[j]
                ax.title.set_text(mode.title() if mode != "" else "Normal")

                if runs:
                    matrix, cs, bs = self.squares[brain_type][mode].get_nr_runs_matrix()
                else:
                    matrix, cs, bs = self.squares[brain_type][mode].get_fitness_matrix()

                ax.imshow(matrix.astype(int), vmin=0, vmax=30 if not runs else 4)
                plt.xticks(list(range(len(bs))), bs)
                plt.yticks(list(range(len(cs))), cs)
                for i, row in enumerate(matrix):
                    for j, val in enumerate(row):
                        if val != 0:
                            ax.text(j, i, round(val), color='black', ha='center', va='center')

        plt.show()

    def plot_all_collapsed(self):
        for brain_type in self.squares.keys():
            for mode in self.squares[brain_type].keys():
                square = self.squares[brain_type][mode]
                self.plot_collapsed(square, brain_type, mode)
        plt.show()

    def plot_collapsed(self, square, brain_type, mode):
        cs = square.get_cs()
        bs = square.get_bs()

        ### B collapsed

        b_lines = {}
        for b in bs:
            b_lines[b] = []

        for c in cs:
            for b in square.runs[c].keys():
                lines = square.get_stat_lines(c, b)
                if len(lines) > 0:
                    for line in lines:
                        b_lines[b].append(line)

        colors = plt.cm.viridis(np.linspace(0, 1, len(bs)))
        transparents = []
        for color in colors:
            transparents.append([color[0], color[1], color[2], 0.3])

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2, sharex = False, sharey = False)
        fig.suptitle(brain_type.title() + " " + mode.title())

        ax1.set_xlabel("Generation")
        ax1.set_ylabel("Fitness")
        ax1.title.set_text("Body mut rates plotted for all control mut rates")

        for i, b in enumerate(b_lines.keys()):
            for line in b_lines[b]:
                ax1.plot(line, color=transparents[i])

        for i, b in enumerate(b_lines.keys()):
            if len(b_lines[b]) > 0:
                ax1.plot(np.sum(b_lines[b], axis=0)/len(b_lines[b]), color=colors[i], linewidth=2)

        ### B collapsed boxplot

        all_last_values = []
        for b, lines in b_lines.items():
            all_last_values.append([])
            for line in lines:
                all_last_values[-1].append(line[-1])

        boxplot(all_last_values, colors, transparents, [str(b) for b in bs], ax2)
        ax2.set_ylabel("Fitness")
        ax2.set_xlabel("Body mutation rate")
        ax2.title.set_text("Body mut rates plotted for all control mut rates")

        ### C collapsed

        c_lines = {}
        for c in cs:
            c_lines[c] = []

        for c in cs:
            for b in square.runs[c].keys():
                lines = square.get_stat_lines(c, b)
                if len(lines) > 0:
                    for line in lines:
                        c_lines[c].append(line)

        colors = plt.cm.viridis(np.linspace(0, 1, len(cs)))
        transparents = []
        for color in colors:
            transparents.append([color[0], color[1], color[2], 0.3])

        ax3.set_xlabel("Generation")
        ax3.set_ylabel("Fitness")
        ax3.title.set_text("Control mut rates plotted for all body mut rates")

        for i, c in enumerate(c_lines.keys()):
            for line in c_lines[c]:
                ax3.plot(line, color=transparents[i])

        for i, c in enumerate(c_lines.keys()):
            if len(c_lines[c]) > 0:
                ax3.plot(np.sum(c_lines[c], axis=0)/len(c_lines[c]), color=colors[i], linewidth=2)

        ### C collapsed boxplot

        all_last_values = []
        for c, lines in c_lines.items():
            all_last_values.append([])
            for line in lines:
                all_last_values[-1].append(line[-1])

        boxplot(all_last_values, colors, transparents, [str(c) for c in cs], ax4)
        ax4.set_ylabel("Fitness")
        ax4.set_xlabel("Control mutation rate")
        ax4.title.set_text("Control mut rates plotted for all body mut rates")

class Square:
    def __init__(self, experiment_folder: str):
        self.experiment_folder = experiment_folder
        self.runs = {}

        self.print_filled = self.treat_spots(self.internal_fill_spot)
        self.print_fitnesses = self.treat_spots(self.internal_fitness_spot)
        self.print_nr_runs = self.treat_spots(self.internal_count_runs_fill)
        self.print_avg_mutated = self.treat_spots(self.internal_avg_mutated_spot)

        self.get_fitness_matrix = self.get_matrix_getter(self.get_fitness)
        self.get_nr_runs_matrix = self.get_matrix_getter(self.get_valid_runs)

    def add_run(self, runNr, c, b):
        if c not in self.runs.keys():
            self.runs[c] = {}

        if b not in self.runs[c].keys():
            self.runs[c][b] = []

        self.runs[c][b].append(runNr)

    def get_stat_lines(self, c, b):
        lines = []

        for runNr in self.runs[c][b]:
            path = f"{self.experiment_folder}/run{runNr}"
            try:
                with open(path+"/data", "rb") as file:
                    data = pickle.load(file)
                    lines.append(data["Fitness"]["Maxs"])
            except:
                pass
        return lines

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
