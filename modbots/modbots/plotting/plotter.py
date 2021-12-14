import numpy as np
import matplotlib.pyplot as plt
import pickle
from skimage.color import hsv2rgb
import seaborn as sns

from modbots.plotting.diversity_measure import diversity

class Plotter:
    def __init__(self):
        self.stats = {}

    def save_stats(self, population):
        nr_modules = []
        fitnesses = []
        for ind in population:
            nr_modules.append(ind.get_nr_modules())
            fitnesses.append(ind.fitness)
        self._save_min_max(nr_modules, "Nr Modules")
        self._save_min_max(fitnesses, "Fitness")
        self._save_stat(diversity(population), "Diversity")

        if "color_id" in population[0].__dict__:
            population = sorted(population, key=lambda x: x.color_id)

        colors = []
        for i, ind in enumerate(population):
            if ind.needs_evaluation and "color" not in ind.__dict__:
                hue = i/(len(population)) * 0.9 + 0.1
                rgb = hsv2rgb([[[hue, 1.0, 1.0]]])[0][0]*255
                ind.color = rgb.astype(int)
                ind.color_id = i
                colors.append(ind.color)
            elif ind.needs_evaluation:
                ind.color = (ind.color.astype(float) * 8 / 10).astype(int)
                colors.append(ind.color)
            else:
                colors.append(ind.color)

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
            plt.xticks(np.arange(0,len(self.stats[key]), max(1, len(self.stats[key])//5, len(self.stats[key])//10 )))
            plt.xlabel("Generation")
            plt.ylabel(key)

            if save_figs:
                name = key.replace(" ", "_")
                plt.savefig(f"{folder}/{name}.png")

        if show_figs:
            plt.show()

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
