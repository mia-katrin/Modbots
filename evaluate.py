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

# EA
from deap import base,tools,algorithms

from individual import Individual
from sideChannelPythonside import SideChannelPythonside

class PackagedUnityEnv:
    def __init__(self, path, seed=42, headless=False, time_scale=None, n_steps=1000, n_start_eval=250):
        self.PATH = path
        self.SEED = seed
        self.HEADLESS = headless
        self.TIME_SCALE = time_scale
        self.N_STEPS = n_steps
        self.N_START_EVAL = n_start_eval

        self.env_pid = None
        self.env = None
        self.side_channel = None

    def _get_env(self):
        pid = multiprocessing.Process()._identity[0]
        if self.env_pid == None:
            self.env_pid = pid
        print("Env is fetched:", self.env_pid, pid)
        if self.side_channel == None:
            self.side_channel = SideChannelPythonside()
        if self.env == None:
            if self.TIME_SCALE != None:
                ec = EngineConfigurationChannel()
                self.env = UnityEnvironment(file_name=self.PATH, seed = self.SEED, side_channels=[self.side_channel, ec], no_graphics = self.HEADLESS, worker_id=pid)
                ec.set_configuration_parameters(time_scale=self.TIME_SCALE)
            else:
                self.env = UnityEnvironment(file_name=self.PATH, seed = self.SEED, side_channels=[self.side_channel], no_graphics = self.HEADLESS, worker_id=pid)
            self.env.reset()
        return self.env, self.side_channel

    def close(self):
        if self.env is not None:
            self.env.close()
            self.env = None
        self.side_channel = None

    def evaluate(self, ind:Individual, force_evaluate=True):
        if not force_evaluate and not ind.needs_evaluation:
            return ind.fitness
        env, side_channel = self._get_env()

        side_channel.send_string(ind.genome_to_str())
        env.reset()

        # Get all nodes of the individual blueprint
        allNodes = []
        ind.traverse_get_list(ind.genomeRoot, allNodes)

        # Ensure all controllers are reset
        for node in allNodes:  # All controllers
            node.controller.reset()

        save_pos = [0,0,0]
        for i in range(self.N_STEPS):
            # Get env observation space. It contains only current fitness
            obs,other = env.get_steps(list(env._env_specs)[0])
            index = list(obs.agent_id_to_index)

            if i == self.N_START_EVAL:
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



# Static across all instances of class
PATH = None
SEED = None
HEADLESS = False
TIME_SCALE = None

# Method to set static variables
def set_env_variables(path, seed=42, headless=False, time_scale=None, n_steps=1000, n_start_eval=250):
    global SEED
    global HEADLESS
    global TIME_SCALE
    global PATH
    global N_STEPS
    global N_START_EVAL
    PATH = path
    SEED = seed
    HEADLESS = headless
    TIME_SCALE = time_scale
    N_STEPS = n_steps
    N_START_EVAL = n_start_eval

# singleton equivalent (unsure if this is true, pool map will spawn several envs
# on different adresses with different variables)
env_pid = None
env = None
side_channel = None
def get_env():
    global env
    global side_channel
    global SEED
    global HEADLESS
    global TIME_SCALE
    global PATH
    global env_pid
    if SEED == None:
        SEED = 42
    #print("Using", SEED, HEADLESS, TIME_SCALE)
    pid = multiprocessing.Process()._identity[0]
    if env_pid == None:
        env_pid = pid
    print("Env is fetched:", env_pid, pid)
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

# Likely won't be able to run this because pool keeps its own copies of envs
def close_env():
    global env
    global sc
    if env is not None:
        env.close()
        env = None
    sc = None

# Evaluate function uses variables of different env instances
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
