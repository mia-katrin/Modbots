import json
from evolve import evolve, get_runNr
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--label", type=str, default=None)
args = parser.parse_args()
if args.label == None:
    run_label = input("Label your run\n> ")
else:
    run_label = args.label

OUTER_ROUNDS = 10
INTERNAL_ROUNDS = 1

def delete_log_folder_content():
    os.system("rm log_folder/*")

def append_runNr(key):
    valid_intervals[run_label][key].append(get_runNr()-1)
    with open("experiments/valid_intervals", "w") as file:
        json.dump(valid_intervals, file)

def run_on_config(conf_name):
    print(conf_name)
    from localconfig import config
    config.read(conf_name)
    config.filename = conf_name

    if conf_name not in valid_intervals[run_label]:
        valid_intervals[run_label][conf_name] = []

    for _ in range(INTERNAL_ROUNDS):
        evolve(config, run_label, show_figs=False)
        append_runNr(conf_name)

        # In order to not use all our memory on rudolph,
        # Delete log_folder content underway
        delete_log_folder_content()

with open("experiments/valid_intervals", "r") as file:
    valid_intervals = json.load(file)

if run_label in valid_intervals:
    raise ValueError("You've named the experiment as something that is already named in valid_intervals. Please choose a different name.")

valid_intervals[run_label] = {
    "Start runNr": get_runNr(),
}

for _ in range(OUTER_ROUNDS):
    run_on_config("baseline.cfg")
    #run_on_config("variable_scale.cfg")
    #run_on_config("gradual.cfg")

valid_intervals[run_label]["End runNr"] = get_runNr()-1
with open("experiments/valid_intervals", "w") as file:
    json.dump(valid_intervals, file)
