import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()

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

    def plot_stats(self, save_figs=False, folder="."):
        if save_figs:
            with open(folder+"/data", "wb") as file:
                pickle.dump(self.stats, file)

        for key in self.stats.keys():
            plt.figure()
            plt.title(key)
            if len(self.stats[key]) > 1:
                for key2 in self.stats[key].keys():
                    plt.plot(self.stats[key][key2], label=key2)
            elif len(self.stats[key]) == 1:
                plt.plot(self.stats[key][0])
            plt.legend()
            plt.xlabel("Generation")
            plt.ylabel(key)

            if save_figs:
                name = key.replace(" ", "_")
                plt.savefig(f"{folder}/{name}.png")

        plt.show()

    def print_stats(self):
        for key in self.stats.keys():
            print()
            if len(self.stats[key]) > 1:
                print(key+":")
                for key2 in self.stats[key].keys():
                    print(key2+":", self.stats[key][key2][-1])
            elif len(self.stats[key]) == 1:
                print(key+":",self.stats[key][0][-1])
            print()
