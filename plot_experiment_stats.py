import json
import pickle
import matplotlib.pyplot as plt
import numpy as np

colors = {
    'sine.cfg':"navajowhite",
    'sine.cfg_avg':"orange",
    'ctrnn.cfg':"paleturquoise",
    'ctrnn.cfg_avg':"lightseagreen",
    'decentr_ctrnn.cfg':"thistle",
    'decentr_ctrnn.cfg_avg':"magenta"
}

linestyles = {
    'sine.cfg':"dashdot",
    'sine.cfg_avg':"orange",
    'ctrnn.cfg':"dashed",
    'ctrnn.cfg_avg':"lightseagreen",
    'decentr_ctrnn.cfg':"dotted",
    'decentr_ctrnn.cfg_avg':"magenta"
}

with open("experiments/valid_intervals", "r") as file:
    valid_intervals = json.load(file)

experiment = valid_intervals["Test run 7"]

def plot_runs(dataname, stat="Means"):
    plt.figure()
    for cfg in ['sine.cfg', 'ctrnn.cfg', 'decentr_ctrnn.cfg']:
        label = cfg[:-4].replace("_", " ").title()

        average = []
        for runNr in experiment[cfg]:
            path = f"experiments/run{runNr}"
            with open(path+"/data", "rb") as file:
                data = pickle.load(file)

            plt.plot(data[dataname][stat], c=colors[cfg], linestyle=linestyles[cfg], label=label)

            if len(average) == 0:
                average = np.array(data[dataname][stat])
            else:
                average += np.array(data[dataname][stat])
        average = average / len(experiment[cfg])
        plt.plot(average, c=colors[cfg+"_avg"], label=label+" average")

        # Do legend without duplicatinng labels
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())

        title = stat.title() + " of " + dataname.title()
        plt.title(title)

        plt.xlabel("Generation")
        plt.ylabel(dataname.title())

        plt.savefig(title)

plot_runs("Fitness", stat="Means")
plot_runs("Nr Modules", stat="Means")

plt.show()
