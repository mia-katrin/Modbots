import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config_file", type=str)

args = parser.parse_args()

label = args.config_file[:-4].replace("_", " ").title()

if label == "Final":
    label = "Final Sine"

jobname = ""
if label.startswith("Final"):
    for item in label.split(" ")[1:]:
        jobname += item[:3].lower()

with open(jobname + "_job.sh", "w") as file:
    file.write(f"""#!/bin/bash

#SBATCH --job-name={jobname}

#SBATCH --account=ec29

#SBATCH --partition=normal

#SBATCH --time=10:00:00

#SBATCH --ntasks=1

#SBATCH --cpus-per-task=25

#SBATCH --mem-per-cpu=3G

set -o errexit
set -o nounset

source /fp/homes01/u01/ec-mkkvalsu/evolve_unity_env/bin/activate

srun python3 evolve.py -s \"{label}\" --config_file {args.config_file}
""")

print(f"File made: " + jobname + "_job.sh")
