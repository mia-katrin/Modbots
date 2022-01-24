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
	write_to_valid_intervals(run_label, key, get_runNr()-1, liste=True)

def run_on_config(conf_name):
    print(conf_name)
    from localconfig import config
    config.read(conf_name)
    config.filename = conf_name

    for _ in range(INTERNAL_ROUNDS):
        evolve(config, run_label, show_figs=False)
        append_runNr(conf_name)

        # In order to not use all our memory on rudolph,
        # Delete log_folder content underway
        delete_log_folder_content()

def write_to_valid_intervals(run_label, key, value, liste=True):
    valid_intervals = None
    with open("experiments/valid_intervals", "r") as file:
        valid_intervals = json.load(file)

    if run_label not in valid_intervals.keys():
        valid_intervals[run_label] = {}

    if liste:
        if key is in valid_intervals[run_label].keys():
            valid_intervals[run_label][key].append(value)
        else:
            valid_intervals[run_label][key] = [value]
    else:
        valid_intervals[run_label][key] = value

    with open("experiments/valid_intervals", "w") as file:
        json.dump(valid_intervals, file)

write_to_valid_intervals(run_label, "Start runNr", get_runNr(), liste=False)

for _ in range(OUTER_ROUNDS):
    run_on_config("baseline.cfg")
    run_on_config("variable_scale.cfg")
    run_on_config("growing.cfg")
    run_on_config("gradual.cfg")

write_to_valid_intervals(run_label, "End runNr", get_runNr()-1, liste=False)
