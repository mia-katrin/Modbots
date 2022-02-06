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
    "warm red": (216/256, 67/256, 37/256),
    "light warm red": (256/256, 157/256, 127/256),
    "faded orange": (237/256, 162/256, 71/256),
    "green beige": (230/256, 225/256, 188/256),
    "warm turqoise": (87/256, 196/256, 173/256),
    "dark turqoise": (0, 97/256, 100/256),
    "bluish green": (0,158/256, 115/256),
    "reddish purple": (204/256, 121/256, 167/256),
    "light reddish purple": (224/256, 141/256, 187/256)
}

color_pairs = [
    ["lightskyblue", "blue"],
    ["palegreen", colors["bluish green"]],
    [colors["light warm red"], colors["warm red"]],
    ["gold", colors["faded orange"]],
    [colors["warm turqoise"], colors["dark turqoise"]],
    [colors["light reddish purple"], colors["reddish purple"]],
    ["hotpink", "red"],
    ["thistle", "darkviolet"]
]

linestyles = {
    'avg':"solid",
    'normal':"dashed",
}

colors = {}
labels = {}
for i, cfg in enumerate(configs):
    colors[cfg + "_avg"] = color_pairs[i][1]
    colors[cfg] = color_pairs[i][0]

    labels[cfg] = cfg[:-4].replace("_", " ").title()

def get_runs(dataname, stat="Mean"):
    """ Returns the full data of stat for all runs in all configs
    runs = {
        "config 1": [[1,2,3,4,...], [1,2,3,4,...], ...],
        "config 2": [...],
        ...
    }
    """
    runs = {}

    for cfg in configs:
        runs[cfg] = []
        for runNr in experiment[cfg]:
            if "Outliers" not in experiment or runNr not in experiment["Outliers"]:
                path = f"experiments/run{runNr}"
                with open(path+"/data", "rb") as file:
                    data = pickle.load(file)

                runs[cfg].append(
                    data[dataname][stat]
                )
    return runs

def get_averages(runs):
    """ Returns the average of full data of stat for all runs in all configs
    runs = {
        "config 1": [[1,2,3,4,...], [1,2,3,4,...], ...],
        "config 2": [...],
        ...
    }
    Returns:
    runs_avg = {
        "config 1": [1,2,3,4,...],
        "config 2": [...],
        ...
    }
    """
    averages = {}
    for cfg in runs:
        average = []
        for run in runs[cfg]:
            if len(average) == 0:
                average = np.array(run)
            else:
                average += np.array(run)
        averages[cfg] = average / len(runs[cfg])
    return averages

def plot_runs(dataname, stat="Means"):
    runs = get_runs(dataname, stat)
    averages = get_averages(runs)

    fig = plt.figure(figsize=(8,4.5))
    ax = plt.subplot(111)

    for cfg in runs:
        for run in runs[cfg]:
            ax.plot(run, c=colors[cfg], linestyle=linestyles["normal"], label=labels[cfg])
        print("Valid runs:", len(runs[cfg]), cfg)

    for cfg in averages:
        ax.plot(averages[cfg], c=colors[cfg+"_avg"], label=labels[cfg]+" Average", linestyle=linestyles["avg"])

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
    for cfg in averages:
        ax.plot(averages[cfg], c=colors[cfg+"_avg"], label=labels[cfg]+" Average", linestyle=linestyles["avg"])

    plt.title(title + " only Averages")
    plt.xlabel("Generation")
    plt.ylabel(dataname.title())
    plt.legend(loc="center left", bbox_to_anchor=(1,0.5))
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.67, box.height])

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

def print_stats(dataname, stat="Maxs"):
    runs = get_runs(dataname, stat)
    averages = get_averages(runs)

    for cfg in averages:
        print(cfg, "stats:")
        avg = averages[cfg]
        print("Average", stat+":", avg[-1])
        print("Runs:", len(runs[cfg]))


#plot_runs("Fitness", stat="Maxs")
print_stats("Fitness", stat="Maxs")
print_stats("Nr Modules", stat="Means")
#plot_runs("Nr Modules", stat="Means")
#plot_mutation()
#boxplot_of_last("Fitness", "Maxs")

plt.show()
