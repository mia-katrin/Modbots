from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel
from mlagents_envs.base_env import ActionTuple

import numpy as np
import os
import multiprocessing

from modbots.evaluate.sideChannelPythonside import SideChannelPythonside

# Static across all instances of class
PATH = None
SEED = None
HEADLESS = False
TIME_SCALE = None

# Method to set static variables
def set_env_variables(path, log_folder, seed=42, headless=False, time_scale=None, n_steps=1000, n_start_eval=250, torque=0.0):
    global SEED
    global HEADLESS
    global TIME_SCALE
    global PATH
    global N_STEPS
    global N_START_EVAL
    global LOG_FOLDER
    global TORQUE
    PATH = path
    SEED = seed
    HEADLESS = headless
    TIME_SCALE = time_scale
    N_STEPS = n_steps
    N_START_EVAL = n_start_eval
    LOG_FOLDER = log_folder
    TORQUE = torque

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
    global TORQUE
    global env_pid
    if SEED == None:
        SEED = 42
    #print("Using", SEED, HEADLESS, TIME_SCALE)
    #pid = multiprocessing.Process()._identity[0]
    pid = os.getpid() % 65535 # Steinar fix
    if env_pid == None:
        env_pid = pid
    print("Env is fetched:", env_pid, pid)
    if (side_channel == None):
        side_channel = SideChannelPythonside()
    if (env == None):
        param_channel = EnvironmentParametersChannel()
        if TIME_SCALE != None:
            ec = EngineConfigurationChannel()
            env = UnityEnvironment(file_name=PATH, seed = SEED, side_channels=[side_channel, ec, param_channel],no_graphics = HEADLESS, worker_id=pid, log_folder=LOG_FOLDER)
            ec.set_configuration_parameters(time_scale=TIME_SCALE)
            env.reset()
        else:
            env = UnityEnvironment(file_name=PATH, seed = SEED, side_channels=[side_channel, param_channel],no_graphics = HEADLESS, worker_id=pid, log_folder=LOG_FOLDER)
            env.reset()
        param_channel.set_float_parameter("torque", TORQUE)
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
def evaluate(ind, force_evaluate=True):
    if not force_evaluate and not ind.needs_evaluation:
        return ind.fitness

    ind.prepare_for_evaluation()

    env, side_channel = get_env()

    side_channel.send_string(ind.body_to_str())
    env.reset()

    save_pos = [0,0,0]
    for i in range(N_STEPS):
        # Get env observation space
        obs,other = env.get_steps(list(env._env_specs)[0])
        assert len(obs.agent_id) > 0

        if i == N_START_EVAL:
            index = list(obs.agent_id_to_index)
            save_pos = obs[index[0]][0][0][:3]

        # Make action array
        if (i >= 100):
            index = list(obs.agent_id_to_index)
            actions = ind.get_actions(obs[index[0]][0][0][3:])
        else:
            actions = np.zeros(shape=(1,50),dtype=np.float32)

        # Send actions
        env.set_action_for_agent("ModularBehavior?team=0",0,ActionTuple(actions))
        env.step()  # Move the simulation forward

    # Get fitness
    index = list(obs.agent_id_to_index)
    current_pos = obs[index[0]][0][0][:3]

    distance_vec = np.array(current_pos) - np.array(save_pos)
    fitness = np.sqrt(distance_vec[0]**2 + distance_vec[2]**2)

    return fitness
