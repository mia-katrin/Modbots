import json
import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse

# Add arguments
parser = argparse.ArgumentParser(description='Find outliers')
parser.add_argument(
    'label',
    type = str,
    help='The label to check'
)

args = parser.parse_args()

with open("experiments/valid_intervals", "r") as file:
    valid_intervals = json.load(file)

experiment = valid_intervals[args.label]

configs = [i for i in experiment.keys() if i != "End runNr" and i != "Start runNr" and i != "Outliers"]

colors = {
    'sine.cfg':"gold",
    'sine.cfg_avg':"orange",
    'ctrnn.cfg':"lightskyblue",
    'ctrnn.cfg_avg':"blue",
    'decentral_ctrnn.cfg':(204/225, 121/225, 167/225),
    'decentral_ctrnn.cfg_avg':(213/225, 94/225, 0),
    'copy_ctrnn.cfg':"palegreen",
    'copy_ctrnn.cfg_avg':(0,158/225, 115/225),
    'pre_ctrnn.cfg':"green",
    'pre_ctrnn.cfg_avg':"green",

    'sine_growing.cfg':"gold",
    'sine_growing.cfg_avg':"orange",
    'ctrnn_growing.cfg':"lightskyblue",
    'ctrnn_growing.cfg_avg':"blue",
    'decentral_ctrnn_growing.cfg':(204/225, 121/225, 167/225),
    'decentral_ctrnn_growing.cfg_avg':(213/225, 94/225, 0),
    'copy_ctrnn_growing.cfg':"palegreen",
    'copy_ctrnn_growing.cfg_avg':(0,158/225, 115/225),
    'pre_ctrnn_growing.cfg':"green",
    'pre_ctrnn_growing.cfg_avg':"green",
}

colors = {
    'baseline.cfg':"gold",
    'baseline.cfg_avg':"orange",
    'variable_scale.cfg':"lightskyblue",
    'variable_scale.cfg_avg':"blue",
    'gradual.cfg':(204/225, 121/225, 167/225),
    'gradual.cfg_avg':(213/225, 94/225, 0),
    'growing.cfg':"palegreen",
    'growing.cfg_avg':(0,158/225, 115/225),
}

linestyles = {
    'sine.cfg':"dashed",
    'ctrnn.cfg':"dashed",
    'decentral_ctrnn.cfg':"dashed",
    'copy_ctrnn.cfg':"dashed",
    'pre_ctrnn.cfg':"dashed",

    'sine_growing.cfg':"dotted",
    'ctrnn_growing.cfg':"dotted",
    'decentral_ctrnn_growing.cfg':"dotted",
    'copy_ctrnn_growing.cfg':"dotted",
    'pre_ctrnn_growing.cfg':"dotted",

    'sine.cfg_avg':"solid",
    'ctrnn.cfg_avg':"solid",
    'decentral_ctrnn.cfg_avg':"solid",
    'copy_ctrnn.cfg_avg':"solid",
    'pre_ctrnn.cfg_avg':"solid",

    'sine_growing.cfg_avg':"dashdot",
    'ctrnn_growing.cfg_avg':"dashdot",
    'decentral_ctrnn_growing.cfg_avg':"dashdot",
    'copy_ctrnn_growing.cfg_avg':"dashdot",
    'pre_ctrnn_growing.cfg_avg':"dashdot",
}
linestyles = {
    'baseline.cfg':"dashed",
    'variable_scale.cfg':"dashed",
    'gradual.cfg':"dashed",
    'growing.cfg':"dashed",

    'baseline.cfg_avg':"solid",
    'variable_scale.cfg_avg':"solid",
    'gradual.cfg_avg':"solid",
    'growing.cfg_avg':"solid"
}

def plot_runs(dataname, stat="Means"):
    fig = plt.figure(figsize=(8,4.5))
    ax = plt.subplot(111)
    averages = []
    labels = []

    last_values = []
    for cfg in configs:
        last_values.append([])

        label = cfg[:-4].replace("_", " ").title()
        labels.append(label)

        average = []
        nr_valid_runs = 0
        for runNr in experiment[cfg]:
            if "Outliers" not in experiment or runNr not in experiment["Outliers"]:
                nr_valid_runs += 1
                path = f"experiments/run{runNr}"
                with open(path+"/data", "rb") as file:
                    data = pickle.load(file)

                last_values[-1].append(data[dataname][stat][-1])

                ax.plot(data[dataname][stat], c=colors[cfg], linestyle=linestyles[cfg], label=label)

                if len(average) == 0:
                    average = np.array(data[dataname][stat])
                else:
                    average += np.array(data[dataname][stat])
        print("Valid runs:", nr_valid_runs, cfg)
        averages.append(average / nr_valid_runs)

    for avg, label, cfg in zip(averages, labels, configs):
        ax.plot(avg, c=colors[cfg+"_avg"], label=label+" Average", linestyle=linestyles[cfg+"_avg"])

    # Do legend without duplicatinng labels
    handles, labels2 = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels2, handles))
    plt.legend(by_label.values(), by_label.keys(), loc="center left", bbox_to_anchor=(1,0.5))
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.67, box.height])

    title = stat.title() + " of " + dataname.title()
    plt.title(title)

    plt.xlabel("Generation")
    plt.ylabel(dataname.title())

    plt.savefig(title.replace(" ", "_"))

    fig = plt.figure(figsize=(8,4.5))
    ax = plt.subplot(111)
    for avg, cfg in zip(averages, configs):
        label = cfg[:-4].replace("_", " ").title()
        ax.plot(avg, c=colors[cfg+"_avg"], label=label+" Average", linestyle=linestyles[cfg+"_avg"])

    plt.title(title + " only Averages")
    plt.xlabel("Generation")
    plt.ylabel(dataname.title())
    plt.legend(loc="center left", bbox_to_anchor=(1,0.5))
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.67, box.height])
    #plt.legend()

    plt.savefig((title + " only Averages").replace(" ", "_"))

def boxplot_of_last(dataname, stat="Means"):
    last_values = []
    labels = []
    for cfg in configs:
        last_values.append([])

        label = cfg[:-4].replace("_", " ").title()
        labels.append(label)

        for runNr in experiment[cfg]:
            if "Outliers" not in experiment or runNr not in experiment["Outliers"]:
                path = f"experiments/run{runNr}"
                with open(path+"/data", "rb") as file:
                    data = pickle.load(file)

                last_values[-1].append(data[dataname][stat][-1])

    plt.figure()
    boxplot(
        last_values,
        [colors[cfg+"_avg"] for cfg in configs],
        [colors[cfg] for cfg in configs],
        labels=labels
    )
    plt.xlabel("Controller")
    plt.ylabel(f"Last {dataname.lower()} {stat.lower()} in evolution")
    plt.xticks(rotation = 15)
    plt.title(f"Last {dataname} {stat} in evolution, comparing controllers".title())
    plt.savefig(f"{dataname}_{stat}_boxplot")

def plot_mutation():
    changes_cfgs = []
    changes_sizes = []
    labels = []
    for cfg in configs:
        labels.append(
            cfg[:-4].replace("_", " ").title()
        )

        changes_list = []
        changes_sizes_list = []

        for runNr in experiment[cfg]:
            if "Outliers" not in experiment or runNr not in experiment["Outliers"]:
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

        changes_cfgs.append(changes_list)
        changes_sizes.append(changes_sizes_list)

    plt.figure()
    boxplot(
        changes_cfgs,
        [colors[cfg+"_avg"] for cfg in configs],
        [colors[cfg] for cfg in configs],
        labels=labels
    )
    plt.xlabel("Controller")
    plt.ylabel("Percentage of generations")
    plt.xticks(rotation = 15)
    plt.title("Percentage of generations that resulted in a new max individual")
    plt.savefig("Percent_of_Generations")

    plt.figure()
    boxplot(
        changes_sizes,
        [colors[cfg+"_avg"] for cfg in configs],
        [colors[cfg] for cfg in configs],
        labels=labels
    )
    plt.xlabel("Controller")
    plt.ylabel("Size of change")
    plt.xticks(rotation = 15)
    plt.title("The average size of changes")
    plt.savefig("Average_Size")

def boxplot(data, edge_color, fill_color, labels):
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

plot_runs("Fitness", stat="Maxs")
plot_runs("Nr Modules", stat="Means")
plot_mutation()
boxplot_of_last("Fitness", "Maxs")

plt.show()
