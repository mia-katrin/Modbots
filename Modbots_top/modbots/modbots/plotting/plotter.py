import numpy as np
import matplotlib.pyplot as plt
import pickle
from skimage.color import hsv2rgb
import seaborn as sns
from random import choice, random

from modbots.plotting.diversity_measure import diversity
from modbots.util import traverse_get_list

class Plotter:
    def __init__(self):
        self.stats = {}

        self.colordown = True

    def nr_mutated(self, population):
        nr_mutated = 0
        for ind in population:
            if ind.needs_evaluation:
                nr_mutated += 1
        return nr_mutated

    def save_stats(self, population):
        nr_modules = []
        fitnesses = []
        mean_scales = []
        for ind in population:
            nr_modules.append(ind.get_nr_modules())
            fitnesses.append(ind.fitness)

            mean_scales.append(0)
            allModules = []
            traverse_get_list(ind.body.root, allModules)
            for module in allModules:
                mean_scales[-1] += module.scale

            mean_scales[-1] /= len(allModules)

        self._save_min_max(nr_modules, "Nr Modules")
        self._save_min_max(fitnesses, "Fitness")
        self._save_min_max(mean_scales, "Mean Scales")
        try:
            self._save_stat(diversity(population), "Diversity")
        except:
            print("Diversity measure does not work")
            self._save_stat(0, "Diversity")
        self._save_stat(self.nr_mutated(population), "Nr Mutated")

        if hasattr(population[0], "color_id"):
            population = sorted(population, key=lambda x: x.color_id)

        L = 1/len(population)
        H = min(0.01, L)
        def mutate_color(ind, i):
            if hasattr(ind, "color"):
                h, s, v = ind.color
                h = (h + H) % 1.0
                id = ind.color_id
                ind.color_id = id - ((np.floor(id + 1) - id) / 2)
            else:
                h = i * L
                v = 1.0
                ind.color_id = i
            s = random() * 0.5 + 0.5
            ind.color = [h, s, v]


        colors = []
        for i, ind in enumerate(population):
            if ind.needs_evaluation:
                mutate_color(ind, i)

            colors.append(
                (hsv2rgb([[ind.color]])[0][0]*255).astype(int)
            )

        self._save_image_column(colors, "Population Heritage")

    def _save_image_column(self, column, internal_name):
        if internal_name not in self.stats:
            self.stats[internal_name] = []

        self.stats[internal_name].append(column)

    def _save_stat(self, value, internal_name):
        if internal_name not in self.stats:
            self.stats[internal_name] = [[]]

        self.stats[internal_name][0].append(value)

    def _save_min_max(self, liste, internal_name):
        if internal_name not in self.stats:
            self.stats[internal_name] = {"Mins":[], "Maxs":[], "Means":[], "Medians":[]}
        self.stats[internal_name]["Mins"].append(
            np.min(liste)
        )
        self.stats[internal_name]["Maxs"].append(
            np.max(liste)
        )
        self.stats[internal_name]["Means"].append(
            np.mean(liste)
        )
        self.stats[internal_name]["Medians"].append(
            np.median(liste)
        )

    def plot_stats(self, save_figs=False, show_figs=True, folder="."):
        if save_figs:
            with open(folder+"/data", "wb") as file:
                pickle.dump(self.stats, file)

        for key in self.stats.keys():
            plt.figure()
            plt.title(key)
            if key == "Population Heritage":
                plt.imshow(
                    np.transpose(np.array(self.stats[key]), [1,0,2])
                )
            elif len(self.stats[key]) > 1:
                for key2 in self.stats[key].keys():
                    plt.plot(self.stats[key][key2], label=key2)
            elif len(self.stats[key]) == 1:
                plt.plot(self.stats[key][0])
            if key != "Population Heritage": plt.legend()
            plt.xticks(np.arange(0,len(self.stats["Diversity"][0]), max(1, len(self.stats["Diversity"][0])//5, len(self.stats["Diversity"][0])//10 )))
            plt.xlabel("Generation")
            plt.ylabel(key)

            if save_figs:
                name = key.replace(" ", "_")
                plt.savefig(f"{folder}/{name}.png")

        if show_figs:
            plt.show()
        plt.close("all")

    def print_stats(self):
        for key in self.stats.keys():
            print()
            if key == "Population Heritage":
                print(
                    "Population Heritage:",
                    len(
                        np.unique(
                            self.stats[key][-1],
                            axis=0
                        )
                    )
                )
            elif len(self.stats[key]) > 1:
                print(key+":")
                for key2 in self.stats[key].keys():
                    print(key2+":", self.stats[key][key2][-1])
            elif len(self.stats[key]) == 1:
                print(key+":",self.stats[key][0][-1])
            print()
