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
ind = Individual("0.9827883283910999,0.7623205770024175,0.12472040388367822,-0.03237059932746522,-0.44357218740204796|[|M0,270,2.82789167506795,0.6226389541397802,0.7454912840716192,0.7679360601334477,0.1251297581055617|[|[|M0,0,2.527833652938718,0.8308429558748411,0.6092275683743622,0.10281495836113441,-0.7332221097654048|]|M1,180,2.392004405916652,0.10636445271542949,-0.18718837192239612,0.7489287356384984,-0.35447793368333835|M0,270,0.1,0.0,0.0,0.0,0.0|]|M2,0,2.8862079403996987,0.7629142179292552,-0.24884317429354907,-0.6380241280555563,0.2754699521419204|]|M1,180,2.25957061259499,0.9790951393756367,0.7689702556322879,0.3114746889953304,0.15106385583765247|[|M1,90,0.2664530628490184,0.17402557139280328,-0.30867800711533944,0.8089123408797243,0.021832502217644434|]|M2,0,1.7005289522616578,0.8744819113073935,0.4596502283393744,-0.48537357679509896,0.2761006937139461|")
set_env_variables(PATH, seed=42, headless=False)
print("Starting:", time.time()-start)

start = time.time()
fitness = evaluate(ind)
print("Evaluating:", time.time()-start)
print(f"We got fitness {fitness}")

start = time.time()
close_env()
print("Closing:", time.time()-start)
