import time

from sideChannelPythonside import SideChannelPythonside
from individual import Individual
from evaluate import get_env, evaluate, close_env, set_env_variables, N_STEPS

print("We start")
start = time.time()
ind = Individual("1.2602734001917675,0.49826408321435656,0.7585531032323451,-0.9652479923072674,-0.5921748573296166|[|M1,180,0.9448383252604702,0.7974693922991731,-0.9877384576789998,-0.3487985147502699,0.7007540611897942|]|M2,180,1.0553850947916277,0.7959127053488967,-0.9903727573579348,-0.027820667505639385,0.32977202555622553|M2,180,1.967879543285281,0.025627966553748327,0.41421925996350617,0.12920232000158394,0.469308519304265|")
set_env_variables(seed=42, headless=False)
print("Starting:", time.time()-start)

start = time.time()
fitness = evaluate(ind)
print("Evaluating:", time.time()-start)
print(f"We got fitness {fitness}")

start = time.time()
close_env()
print("Closing:", time.time()-start)
