import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("-br", "--brain", type=str)
parser.add_argument("-m", "--mode", type=str)
parser.add_argument("--cs", "-c", nargs='+', required=True)
parser.add_argument("--bs", "-b", nargs='+', required=True)

args = parser.parse_args()
brain = args.brain.title()
mode = args.mode.title()

bs = ""
for b in args.bs:
    bs += b + " "
cs = ""
for c in args.cs:
    cs += c + " "

label = f"{brain}, {mode}: Tuning " # and then a number
highest_tune_nr = 0
found = False

valid_intervals = None
with open("experiments/valid_intervals", "r") as file:
    valid_intervals = json.load(file)

for exp_label in valid_intervals.keys():
    if exp_label.startswith(label):
        found = True
        number = exp_label[len(label):]
        number = int(number)

        if number > highest_tune_nr:
            highest_tune_nr = number
if found:
    highest_tune_nr += 1

label += str(highest_tune_nr)

jobname = brain[0] + mode[0] + mode[2] + "Tun" + str(highest_tune_nr)

with open("tune_job.sh", "w") as file:
    file.write(f"""#!/bin/bash

#SBATCH --job-name={jobname}

#SBATCH --account=ec29

#SBATCH --partition=normal

#SBATCH --time=30:00:00

#SBATCH --ntasks=1

#SBATCH --cpus-per-task=25

#SBATCH --mem-per-cpu=1G

set -o errexit
set -o nounset

source /fp/homes01/u01/ec-mkkvalsu/evolve_unity_env/bin/activate

srun python3 run_several.py -l \"{label}\" -m {mode.lower()} -br {brain.lower()} -b {bs}-c {cs}
""")

print("File made")
