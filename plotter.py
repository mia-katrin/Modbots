import numpy as np
import matplotlib.pyplot as plt

class Plotter:
    def __init__(self):
        self.stats = {}

    def save_stats(self, population):
        nr_modules = []
        fitnesses = []
        for ind in population:
            nr_modules.append(ind.get_nr_expressed_modules())
            fitnesses.append(ind.fitness)
        self._save_stats(nr_modules, "Nr Modules")
        self._save_stats(fitnesses, "Fitness")

    def _save_stats(self, liste, internal_name):
        if internal_name not in self.stats:
            self.stats[internal_name] = [[],[],[],[]]
        self.stats[internal_name][0].append(
            np.min(liste)
        )
        self.stats[internal_name][1].append(
            np.max(liste)
        )
        self.stats[internal_name][2].append(
            np.mean(liste)
        )
        self.stats[internal_name][3].append(
            np.median(liste)
        )

    def plot_stats(self, save_figs=False, folder="."):
        for key in self.stats.keys():
            plt.figure()
            plt.title(key)
            plt.plot(self.stats[key][0], label="Mins")
            plt.plot(self.stats[key][1], label="Maxs")
            plt.plot(self.stats[key][2], label="Means")
            plt.plot(self.stats[key][3], label="Median")
            plt.legend()

            if save_figs:
                plt.savefig(f"{folder}/{key}.png")

        plt.show()

    def print_stats(self):
        for key in self.stats.keys():
            print()
            print(key+":")
            print("Worst:",  self.stats[key][0][-1])
            print("Mean:",   self.stats[key][1][-1])
            print("Median:", self.stats[key][2][-1])
            print("Best:",   self.stats[key][3][-1])
            print()
