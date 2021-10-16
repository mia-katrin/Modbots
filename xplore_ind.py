import time

from sideChannelPythonside import SideChannelPythonside
from individual import Individual
from evaluate import get_env, evaluate, close_env, set_env_variables

import argparse

# Add arguments
parser = argparse.ArgumentParser(description='Explore some boys')
parser.add_argument(
    'config_file',
    type=str,
    help='The config file to configure this evolution'
)

with open(parser.parse_args().config_file, "r") as file:
    for line in file:
        exec(line)
        print(line)

print("We start")
start = time.time()
ind = Individual("1.2685027908474067,0.6330647494678748,0.7514770066135259,0.05946973698473923,0.16123647192803037|[|[|M0,270,0.1,0.0,0.0,0.0,0.0|]|M1,90,0.9454385007438737,0.07941723195434847,0.44380979909213036,0.09423944081015567,-0.6833995972746172|]|M2,0,1.3205113620782574,0.8289452662517381,-0.7930996918359272,0.879697412462737,-0.45201743624290414|M2,90,2.4975314740982397,0.20489618361202022,0.33882671319207325,-0.09256093655794428,0.5756419446564767|M0,270,1.275160575630757,0.531212789804637,-0.3969466470229286,0.6594911134834489,-0.5635117052332579|M1,180,0.1,0.0,0.0,0.0,0.0|")
set_env_variables(PATH, seed=SEED, headless=HEADLESS, n_steps=N_STEPS, n_start_eval=N_START_EVAL)
print("Starting:", time.time()-start)

start = time.time()
fitness = evaluate(ind)
print("Evaluating:", time.time()-start)
print(f"We got fitness {fitness}")

start = time.time()
close_env()
print("Closing:", time.time()-start)
