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
def set_env_variables(config=None, path=None, log_folder=None, seed=None, headless=None, time_scale=None, n_steps=None, n_start_eval=None, torque=None, env_enum=None):
    global SEED
    global HEADLESS
    global TIME_SCALE
    global PATH
    global N_STEPS
    global N_START_EVAL
    global LOG_FOLDER
    global TORQUE
    global ENV_ENUM

    PATH       = path         if path != None           else config.files.build_path
    LOG_FOLDER = log_folder   if log_folder != None     else config.files.log_folder
    SEED       = seed         if seed != None           else config.experiment.seed
    HEADLESS   = headless     if headless != None       else config.experiment.headless
    N_STEPS    = n_steps      if n_steps != None        else config.evaluation.n_steps
    N_START_EVAL = n_start_eval if n_start_eval != None else config.evaluation.n_start_eval
    TIME_SCALE = time_scale   if time_scale != None     else config.evaluation.time_scale
    ENV_ENUM   = env_enum     if env_enum != None       else config.evaluation.env_enum
    TORQUE     = torque       if torque != None         else config.individual.torque

ENV_SEEDS = [0.0]
def set_env_seeds(env_seeds):
    global ENV_SEEDS
    ENV_SEEDS = env_seeds

# singleton equivalent (unsure if this is true, pool map will spawn several envs
# on different adresses with different variables)
env_pid = None
env = None
side_channel = None
param_channel = None
def get_env():
    global env
    global side_channel
    global param_channel
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
    pid = os.getpid() % 10000 # Steinar fix
    if env_pid == None:
        env_pid = pid
    #print("Env is fetched:", env_pid, pid)
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
        param_channel.set_float_parameter("envEnum", ENV_ENUM)
    return env, side_channel, param_channel

# Likely won't be able to run this because pool keeps its own copies of envs
def close_env():
    global env
    global sc
    if env is not None:
        env.close()
        env = None
    sc = None

# Evaluate function uses variables of different env instances
def evaluate(ind, force_evaluate=True, record=False):
    if not force_evaluate and not ind.needs_evaluation:
        return ind.fitness

    ind.prepare_for_evaluation()

    env, side_channel, param_channel = get_env()

    fitness = 0
    for env_seed in ENV_SEEDS:

        side_channel.send_string(ind.body_to_str())
        param_channel.set_float_parameter("seed", env_seed)
        env.reset()

        if record:
            side_channel.send_string("Record, /Users/mia-katrinkvalsund/Desktop/Skole/master_project/Modbots/video")

        # Action plotting
        #lines = [[] for _ in range(ind.get_nr_modules())]

        save_pos = [0,0,0]
        last_100 = [0,0,0]
        for i in range(N_STEPS):
            # Get env observation space
            obs,other = env.get_steps(list(env._env_specs)[0])
            assert len(obs.agent_id) > 0

            if i == N_START_EVAL:
                index = list(obs.agent_id_to_index)
                save_pos = obs[index[0]][0][0][:3]

                last_100 = obs[index[0]][0][0][:3]
            elif i > N_START_EVAL+9 and i % 10 == 0:
                index = list(obs.agent_id_to_index)

                if np.allclose(obs[index[0]][0][0][:3], last_100, atol=0.1):
                    print(f"Broke early {i}")
                    break

                last_100 = obs[index[0]][0][0][:3]

            # Make action array
            if (i >= 10):
                index = list(obs.agent_id_to_index)
                actions = ind.get_actions(obs[index[0]][0][0][3:])
            else:
                actions = np.zeros(shape=(1,50),dtype=np.float32)

            # Action plotting
            #for i, liste in enumerate(lines):
            #    liste.append(actions[0,i])

            # Send actions
            env.set_action_for_agent("ModularBehavior?team=0",0,ActionTuple(actions))
            env.step()  # Move the simulation forward

        if record:
            side_channel.send_string("Stop recording")

        # Action plotting
        #import matplotlib.pyplot as plt
        #for line in lines:
        #    plt.plot(line)
        #plt.show()

        # Get fitness
        index = list(obs.agent_id_to_index)
        current_pos = obs[index[0]][0][0][:3]

        # This all should work even when the value sentback is how far into
        # the maze/corridor it has gotten, however be careful
        distance_vec = np.array(current_pos) - np.array(save_pos)
        fitness += np.sqrt(distance_vec[0]**2 + distance_vec[2]**2)

    return fitness / len(ENV_SEEDS)
