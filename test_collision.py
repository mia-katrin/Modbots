"""from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from mlagents_envs.side_channel.side_channel import (
    SideChannel,
    IncomingMessage,
    OutgoingMessage,
)
import os

from sideChannelPythonside import SideChannelPythonside
from individual import Node, Individual
from evolve import evaluate

root = Node(0,[0,0,0,0])

root.children[0] = Node(0,[0,0,0,0])
root.children[0].children[0] = Node(0,[0,0,0,0])
root.children[0].children[0].children[0] = Node(0,[0,0,0,0])
root.children[0].children[0].children[0].children[0] = Node(0,[0,0,0,0])
root.children[0].children[0].children[0].children[0].children[0] = Node(0,[0,0,0,0])
root.children[0].children[0].children[0].children[0].children[0].children[0] = Node(0,[0,0,0,0])

ind = Individual()
ind.genomeRoot = root

# Create the channel
sc = SideChannelPythonside()
#ec = EngineConfigurationChannel()

# We start the communication with the Unity Editor and pass the string_log side channel as input
PATH = os.path.expanduser("~/Desktop/Skole/master_project/Modbots_v2/Build")
env = UnityEnvironment(file_name=PATH, seed=1, side_channels=[sc], no_graphics=False)

#ec.set_configuration_parameters(time_scale=2.0)
sc.send_string("Hello")

print(
    "Fitness:",
    evaluate(ind, env, sc),
    "\nModules:",
    ind.get_nr_expressed_modules(),
    "\n",
    ind.genome_to_str()
)"""
