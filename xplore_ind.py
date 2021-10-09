import time

from sideChannelPythonside import SideChannelPythonside
from individual import Individual
from evaluate import get_env, evaluate, close_env, set_env_variables, N_STEPS

print("We start")
start = time.time()
ind = Individual("2.9886451619219216,0.03013316770901686,0.7813247042183409,-0.6525333935166522,-0.08257504588372289|[|[|M0,270,2.985054718137507,0.3859752009346328,0.18040501573693146,-0.9674347567612309,0.04517981788762793|M1,0,0.1,0.0,0.0,0.0,0.0|]|M1,270,0.9575148049613686,0.9115526327291905,-0.8941877211695131,0.5157881394813759,-0.34670151531668325|]|M2,180,1.6133920441325122,0.5761833952375693,0.34815499930675964,0.2067700494675604,-0.09239543242907233|")
set_env_variables(seed=42, headless=False)
print("Starting:", time.time()-start)

start = time.time()
fitness = evaluate(ind)
print("Evaluating:", time.time()-start)
print(f"We got fitness {fitness}")

start = time.time()
close_env()
print("Closing:", time.time()-start)
