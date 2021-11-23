# This script does not need to know how many frames there are

import cv2
import numpy as np
import pyautogui
import os

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

ind = Individual.unpack_ind("bestInd/ind", config)

env, sc = get_env()
evaluate(ind)
env.reset()

close_env()

"""img_array = []
i = 0
img = cv2.imread(f"video/frame{i}.png")
height, width, layers = img.shape
size = (width,height)

while img is not None:
    img_array.append(img)
    i += 1

    img = cv2.imread(f"video/frame{i}.png")

out = cv2.VideoWriter('project.mp4',cv2.VideoWriter_fourcc(*'MP4V'), 30, size)

for i in range(len(img_array)):
    out.write(img_array[i])
out.release()"""
