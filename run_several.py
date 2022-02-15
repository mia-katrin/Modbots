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

OUTER_ROUNDS = 1
INTERNAL_ROUNDS = 4

configs = list()

########## COPY ##########

cs = [0.08,0.08,0.08,0.08,0.08,0.08]
bs = [0.08,0.16,0.24,0.32,0.48,0.64]

mode = "gradual"
brain = "copy"

########## COPY ##########

if brain != "":
    brain = "_" + brain
for c, b in zip(cs, bs):
    c = str(c)[2:]
    b = str(b)[2:]
    configs.append(f"0{c}c0{b}b{mode}{brain}.cfg")
    print("Doing", f"0{c}c0{b}b{mode}{brain}.cfg")


runNr = get_runNr()
with open("experiments/runNr.txt", "w") as file:
    file.write(f"{runNr + len(configs)*OUTER_ROUNDS*INTERNAL_ROUNDS}")
    file.close()

def delete_log_folder_content():
    os.system("rm log_folder/*")

def append_runNr(key):
	write_to_valid_intervals(run_label, key, runNr, liste=True)

def run_on_config(conf_name):
    global runNr

    print(conf_name)
    from localconfig import config # Sorry about this
    config.read(conf_name)
    config.filename = conf_name

    for _ in range(INTERNAL_ROUNDS):
        failed = 0
        try_again = True
        while failed < 10 and try_again:
            try:
                evolve(config, run_label, show_figs=False, runNr=runNr)
                try_again = False
            except:
                failed += 1
        append_runNr(conf_name)
        runNr += 1

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
        if key in valid_intervals[run_label].keys():
            valid_intervals[run_label][key].append(value)
        else:
            valid_intervals[run_label][key] = [value]
    else:
        valid_intervals[run_label][key] = value

    with open("experiments/valid_intervals", "w") as file:
        json.dump(valid_intervals, file)

write_to_valid_intervals(run_label, "Start runNr", runNr, liste=False)
write_to_valid_intervals(run_label, "End runNr", runNr + len(configs)*OUTER_ROUNDS*INTERNAL_ROUNDS-1, liste=False)

for _ in range(OUTER_ROUNDS):
    for cfg in configs:
        run_on_config(cfg)
