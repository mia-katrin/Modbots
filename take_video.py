# This script does not need to know how many frames there are

import cv2
import numpy as np
import pyautogui
import os
import time

from mlagents_envs.base_env import ActionTuple

from modbots.evaluate import set_env_variables, close_env, evaluate, get_env
from modbots.creature_types.configurable_individual import Individual

from config_util import get_config

config = get_config()

set_env_variables(
    config.files.build_path,
    config.files.log_folder,
    seed=config.experiment.seed,
    headless=config.experiment.headless,
    n_steps=config.evaluation.n_steps,
    n_start_eval=config.evaluation.n_start_eval,
    time_scale=config.evaluation.time_scale
)

def record_evaluate(ind):
    fitness = evaluate(ind, force_evaluate=True, record=True)
    if ind.fitness == -1:
        print("Has no recorded performance")
    elif  ind.fitness != fitness:
        print("Recording has hindered performance")
    else:
        print("Equal performance in recording")

    img_array = []

    img = cv2.imread(f"video/frame0.png")
    height, width, layers = img.shape
    size = (width,height)

    i = 0
    while img is not None:
        img_array.append(img)
        i += 1

        img = cv2.imread(f"video/frame{i}.png")

    out = cv2.VideoWriter('project.mp4',cv2.VideoWriter_fourcc(*'MP4V'), 60, size)

    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

ind = Individual.unpack_ind("bestInd/ind", config)
ind.prepare_for_evaluation()

record_evaluate(ind)

"""env, side_channel = get_env()

side_channel.send_string(ind.body_to_str())
env.reset()

side_channel.send_string("Record, /Users/mia-katrinkvalsund/Desktop/Skole/master_project/Modbots/video")

for i in range(config.evaluation.n_steps):
    # Get env observation space
    obs,other = env.get_steps(list(env._env_specs)[0])

    # Make action array
    if (i >= 100):
        index = list(obs.agent_id_to_index)
        actions = ind.get_actions(obs[index[0]][0][0][3:])
    else:
        actions = np.zeros(shape=(1,50),dtype=np.float32)

    # Send actions
    env.set_action_for_agent("ModularBehavior?team=0",0,ActionTuple(actions))
    env.step()  # Move the simulation forward

side_channel.send_string("Stop recording")

env.reset()

time.sleep(3)"""
