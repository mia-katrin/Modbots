import time

from sideChannelPythonside import SideChannelPythonside
from individual import Individual
from evaluate import get_env, evaluate, close_env, set_env_variables

import argparse
# Add arguments
parser = argparse.ArgumentParser(description='Evolve some boys')
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
ind = Individual("2.0269899848085755,0.6680172777175727,0.5092578564279391,0.9123078353866878,0.2836876496412799|[|M0,0,1.8334160612206403,0.021988668781237508,0.4014423422344845,0.3679522822487904,-0.789715286851295|M1,90,2.640594221304898,0.9183199838495508,-0.16375768302867377,-0.8235091877599225,-0.20872644911452376|]|M2,180,1.4817429248132439,0.156175219232765,0.15490029665371963,-0.5690276416947786,0.7094564278550091|M1,0,1.7109147336748753,0.7345109930902801,-0.2066668538939973,0.3860555770852674,-0.13814066782525347|M0,270,2.793301542561685,0.9144402978747757,-0.5310249039244355,-0.8661316652400641,0.5345793872269149|M1,0,0.1,0.0,0.0,0.0,0.0|")
set_env_variables(PATH, seed=42, headless=False)
print("Starting:", time.time()-start)

start = time.time()
fitness = evaluate(ind)
print("Evaluating:", time.time()-start)
print(f"We got fitness {fitness}")

start = time.time()
close_env()
print("Closing:", time.time()-start)
