import json
from evolve import evolve, get_runNr
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--label", type=str, required=True)
parser.add_argument("--mode", "-m", type=str)
parser.add_argument("--brain", "-br", type=str)
parser.add_argument("--cs", "-c", nargs='+', required=False)
parser.add_argument("--bs", "-b", nargs='+', required=False)
parser.add_argument("--outer_rounds", "-o", type=int, default=1)
parser.add_argument("--inner_rounds", "-i", type=int, default=4)
parser.add_argument(
    '--final', '-f',
    action="store_true",
    help='Final run? Yields different config name and generations',
    default=False
)

args = parser.parse_args()

run_label = args.label

OUTER_ROUNDS = args.outer_rounds
INTERNAL_ROUNDS = args.inner_rounds

configs = list()

mode = args.mode if args.mode != "normal" else ""
brain = args.brain if args.brain != "sine" else ""

if brain != "":
    brain = "_" + brain

if args.final:
    if mode != "":
        mode = "_" + mode
    configs.append(f"final{mode}{brain}.cfg")
    print("Doing", f"final{mode}{brain}.cfg")
else:
    cs = [float(i) for i in args.cs]
    bs = [float(i) for i in args.bs]

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
    if config is None:
        raise Exception(f"The config {conf_name} does not exist!")
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
        if failed >= 10:
            print("\n\nEvolution has failed\n\n")
        #append_runNr(conf_name)
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

#write_to_valid_intervals(run_label, "Start runNr", runNr, liste=False)
#write_to_valid_intervals(run_label, "End runNr", runNr + len(configs)*OUTER_ROUNDS*INTERNAL_ROUNDS-1, liste=False)

for _ in range(OUTER_ROUNDS):
    for cfg in configs:
        run_on_config(cfg)
