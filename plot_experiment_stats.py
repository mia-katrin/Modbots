import json
import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

configs = [
    'sine.cfg',
    'ctrnn.cfg',
    'decentr_ctrnn.cfg',
    'copy_ctrnn.cfg',

    'sine_growing.cfg',
    'ctrnn_growing.cfg',
    'decentr_ctrnn_growing.cfg',
    'copy_ctrnn_growing.cfg',
]

colors = {
    'sine.cfg':"navajowhite",
    'sine.cfg_avg':"orange",
    'ctrnn.cfg':"paleturquoise",
    'ctrnn.cfg_avg':"dodgerblue",
    'decentr_ctrnn.cfg':"thistle",
    'decentr_ctrnn.cfg_avg':"magenta",
    'copy_ctrnn.cfg':"palegreen",
    'copy_ctrnn.cfg_avg':"limegreen",

    'sine_growing.cfg':"yellow",
    'sine_growing.cfg_avg':"goldenrod",
    'ctrnn_growing.cfg':"lightskyblue",
    'ctrnn_growing.cfg_avg':"blue",
    'decentr_ctrnn_growing.cfg':"pink",
    'decentr_ctrnn_growing.cfg_avg':"deeppink",
    'copy_ctrnn_growing.cfg':"yellowgreen",
    'copy_ctrnn_growing.cfg_avg':"forestgreen",
}

linestyles = {
    'sine.cfg':"dashed",
    'ctrnn.cfg':"dashed",
    'decentr_ctrnn.cfg':"dashed",
    'copy_ctrnn.cfg':"dashed",

    'sine_growing.cfg':"dotted",
    'ctrnn_growing.cfg':"dotted",
    'decentr_ctrnn_growing.cfg':"dotted",
    'copy_ctrnn_growing.cfg':"dotted",

    'sine.cfg_avg':"solid",
    'ctrnn.cfg_avg':"solid",
    'decentr_ctrnn.cfg_avg':"solid",
    'copy_ctrnn.cfg_avg':"solid",

    'sine_growing.cfg_avg':"dashdot",
    'ctrnn_growing.cfg_avg':"dashdot",
    'decentr_ctrnn_growing.cfg_avg':"dashdot",
    'copy_ctrnn_growing.cfg_avg':"dashdot",
}

with open("experiments/valid_intervals", "r") as file:
    valid_intervals = json.load(file)

experiment = valid_intervals["Test run 13"]

def plot_runs(dataname, stat="Means"):
    plt.figure()
    averages = []
    labels = []
    for cfg in configs:
        label = cfg[:-4].replace("_", " ").title()
        labels.append(label)

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
        averages.append(average / len(experiment[cfg]))

    for avg, label, cfg in zip(averages, labels, configs):
        plt.plot(avg, c=colors[cfg+"_avg"], label=label+" Average", linestyle=linestyles[cfg+"_avg"])

    # Do legend without duplicatinng labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    title = stat.title() + " of " + dataname.title()
    plt.title(title)

    plt.xlabel("Generation")
    plt.ylabel(dataname.title())

    plt.savefig(title.replace(" ", "_"))

    plt.figure()
    for avg, label, cfg in zip(averages, labels, configs):
        plt.plot(avg, c=colors[cfg+"_avg"], label=label+" Average", linestyle=linestyles[cfg+"_avg"])

    plt.title(title + " only Averages")
    plt.xlabel("Generation")
    plt.ylabel(dataname.title())
    plt.legend()

    plt.savefig((title + " only Averages").replace(" ", "_"))

def plot_mutation():
    changes_cfgs = pd.DataFrame()
    changes_sizes = pd.DataFrame()
    labels = []
    for cfg in configs:
        labels.append(
            cfg[:-4].replace("_", " ").title()
        )

        changes_list = []
        changes_sizes_list = []

        for runNr in experiment[cfg]:
            changes = 0
            avg_sizes = 0
            path = f"experiments/run{runNr}"
            with open(path+"/data", "rb") as file:
                data = pickle.load(file)

            max_fitnesses = data["Fitness"]["Maxs"]
            generations = len(max_fitnesses)
            for i in range(1, generations):
                if max_fitnesses[i] != max_fitnesses[i-1]:
                    changes += 1
                    avg_sizes += (max_fitnesses[i] - max_fitnesses[i-1])

            if changes != 0:
                avg_sizes = avg_sizes / changes
            changes_list.append(changes / generations)
            changes_sizes_list.append(avg_sizes)

        changes_cfgs[cfg] = changes_list
        changes_sizes[cfg] = changes_sizes_list

    plt.figure()
    box_plot(
        changes_cfgs,
        [pair[1] for pair in colors.items() if pair[0].endswith("_avg")],
        [pair[1] for pair in colors.items() if not pair[0].endswith("_avg")],
        labels=labels
    )
    plt.xlabel("Controller")
    plt.ylabel("Percentage of generations")
    plt.title("Percentage of generations that resulted in a new max individual")
    plt.savefig("Percent_of_Generations")

    plt.figure()
    box_plot(
        changes_sizes,
        [pair[1] for pair in colors.items() if pair[0].endswith("_avg")],
        [pair[1] for pair in colors.items() if not pair[0].endswith("_avg")],
        labels=labels
    )
    plt.xlabel("Controller")
    plt.ylabel("Size of change")
    plt.title("The average size of changes")
    plt.savefig("Average_Size")

def box_plot(data, edge_color, fill_color, labels):
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

plot_runs("Fitness", stat="Means")
plot_runs("Nr Modules", stat="Means")
plot_mutation()

plt.show()
