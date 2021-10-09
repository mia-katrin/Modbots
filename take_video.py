import cv2
import numpy as np
import pyautogui

# This script does not need to know how many frames there are

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from mlagents_envs.side_channel.side_channel import (
    SideChannel,
    IncomingMessage,
    OutgoingMessage,
)
import numpy as np
import uuid
import os

from sideChannelPythonside import SideChannelPythonside
from individual import Individual

"""# Create the channel
sc = SideChannelPythonside()
ec = EngineConfigurationChannel()

# We start the communication with the Unity Editor and pass the string_log side channel as input
PATH = os.path.expanduser("~/Desktop/Skole/master_project/Modbots_v2/Build")
env = UnityEnvironment(file_name=PATH, seed=1, side_channels=[sc, ec], no_graphics=False)

ec.set_configuration_parameters(time_scale=1.0)
sc.send_string("Hello")

env.reset()
sc.send_string("2.0209275620080414,0.08411636456929772,0.5069916055633181,-0.06909363564282989|M1,0,2.399482972127114,2.3482921505463588,0.8870379283652585,-0.050956473108996314|M2,270,0.48564960582458094,0.5761236668692372,-0.009768328265087223,0.14234995335459366|")
env.reset()
sc.send_string("Record")

for i in range(1000):
    env.step()  # Move the simulation forward
env.close()

img_array = []
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
out.release()
"""
