from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.side_channel import (
    SideChannel,
    IncomingMessage,
    OutgoingMessage,
)
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from mlagents_envs.base_env import ActionTuple

import numpy as np
import uuid
import os
import matplotlib.pyplot as plt
from tqdm import tqdm
import copy
import multiprocessing
import time
#from gym_unity.envs import UnityToGymWrapper

# EA
from deap import base,tools,algorithms

from individual import Individual
from sideChannelPythonside import SideChannelPythonside

# Globals that are changable before start but not during run
N_STEPS = 1000 # Should correspond to modularrobot.base.MaxStep but does not have to
N_START_EVAL = 250
<<<<<<< HEAD
PATH = os.path.expanduser("~/Desktop/Skole/master_project/Modbots_v2/Build")
#PATH = "/uio/hume/student-u22/mkkvalsu/master_project/Modbots_v2/LinuxBuild.x86_64"
=======
PATH = "/uio/hume/student-u22/mkkvalsu/master_project/Modbots_v2/LinuxBuild.x86_64"
print(PATH)
>>>>>>> 1f107e281f73badd889dc2b286a11a74140789a6
# Default globals that can be changed during a run, but won't normally
# Yes this is awful coding, it's needlessly hard to understand
SEED = None
HEADLESS = False
TIME_SCALE = None

def set_env_variables(seed=42, headless=False, time_scale=None):
    global SEED
    global HEADLESS
    global TIME_SCALE
    SEED = seed
    HEADLESS = headless
    TIME_SCALE = time_scale

# singleton equivalent
env = None
side_channel = None
def get_env():
    global env
    global side_channel
    global SEED
    global HEADLESS
    global TIME_SCALE
    if SEED == None:
        SEED = 42
    print("Using", SEED, HEADLESS, TIME_SCALE)
    pid = multiprocessing.Process()._identity[0]
    if (side_channel == None):
        side_channel = SideChannelPythonside()
    if (env == None):
        if TIME_SCALE != None:
            ec = EngineConfigurationChannel()
            env = UnityEnvironment(file_name=PATH, seed = SEED, side_channels=[side_channel, ec],no_graphics = HEADLESS, worker_id=pid)
            ec.set_configuration_parameters(time_scale=TIME_SCALE)
            env.reset()
        else:
            env = UnityEnvironment(file_name=PATH, seed = SEED, side_channels=[side_channel],no_graphics = HEADLESS, worker_id=pid)
            env.reset()
    return env, side_channel

def close_env():
    global env
    global sc
    if env is not None:
        env.close()
        env = None
    sc = None

def evaluate(ind:Individual, force_evaluate=True):
    if not force_evaluate and not ind.needs_evaluation:
        return ind.fitness
    env, side_channel = get_env()

    side_channel.send_string(ind.genome_to_str())
    env.reset()

    # Get all nodes of the individual blueprint
    allNodes = []
    ind.traverse_get_list(ind.genomeRoot, allNodes)

    # Ensure all controllers are reset
    for node in allNodes:  # All controllers
        node.controller.reset()

    save_pos = [0,0,0]
    for i in range(N_STEPS):
        # Get env observation space. It contains only current fitness
        obs,other = env.get_steps(list(env._env_specs)[0])
        index = list(obs.agent_id_to_index)

        if i == N_START_EVAL:
            save_pos = obs[index[0]][0][0]

        # Make action array
        # Zeros over ndarray because ndarray initializes with very small numbers
        # instead of zeros. Unsure if it matters, but it helps for clarity
        actions = np.zeros(shape=(1,50),dtype=np.float32)
        if (i >= 100):
            allNodes = []
            ind.traverse_get_list(ind.genomeRoot, allNodes)

            for j, node in enumerate(allNodes):  # All controllers
                action = node.controller.update(0.05)
                actions[0,j] = action

        # Send actions
        env.set_action_for_agent("ModularBehavior?team=0",0,ActionTuple(actions))
        env.step()  # Move the simulation forward

    # Get fitness
    index = list(obs.agent_id_to_index)
    current_pos = obs[index[0]][0][0]

    distance_vec = np.array(current_pos) - np.array(save_pos)
    fitness = np.sqrt(distance_vec[0]**2 + distance_vec[2]**2)

    return fitness
