import json
from evolve import evolve, get_runNr
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--label", type=str, default=input("Label your run\n> "))
args = parser.parse_args()
run_label = args.label

ROUNDS = 10

def append_runNr(key):
    valid_intervals[run_label][key].append(get_runNr()-1)
    with open("experiments/valid_intervals", "w") as file:
        json.dump(valid_intervals, file)

def run_on_config(conf_name):
    from localconfig import config
    config.read(conf_name)
    config.filename = conf_name

    valid_intervals[run_label][conf_name] = []
    for _ in range(ROUNDS):
        evolve(config, run_label, show_figs=False)
        append_runNr(conf_name)

with open("experiments/valid_intervals", "r") as file:
    valid_intervals = json.load(file)

valid_intervals[run_label] = {
    "Start runNr": get_runNr(),
}

run_on_config("copy_ctrnn_growing.cfg")
run_on_config("sine_growing.cfg")
run_on_config("ctrnn_growing.cfg")
run_on_config("decentr_ctrnn_growing.cfg")
run_on_config("copy_ctrnn.cfg")
run_on_config("sine.cfg")
run_on_config("ctrnn.cfg")
run_on_config("decentr_ctrnn.cfg")

valid_intervals[run_label]["End runNr"] = get_runNr()-1
with open("experiments/valid_intervals", "w") as file:
    json.dump(valid_intervals, file)
