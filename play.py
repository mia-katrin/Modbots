from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel
import os

from modbots.evaluate.sideChannelPythonside import SideChannelPythonside

from config_util import get_config_no_args

import argparse
parser = argparse.ArgumentParser()
parser.add_argument(
    "--choose", "-c",
    action="store_true",
    help='To choose or not',
    default=False
)

filename = None
folder = None
args = parser.parse_args()
if not args.choose:
    filename = "recorded_ind.txt"
else:
    print("Choose a folder:\n")

    path = "recordings"

    choices = []
    for i, folder in enumerate(os.listdir(path)):
        choices.append(folder)
        print(i, ":", folder)
    inp = input(">")

    if not(0 <= int(inp) < len(choices)):
        print("Yo failed")
        assert False

    folder = choices[int(inp)]

    print("Choose recording:\n")

    choices = []
    for i, file in enumerate(os.listdir(path + "/" + folder)):
        choices.append(file)
        print(i, ":", file)
    inp = input(">")

    if not(0 <= int(inp) < len(choices)):
        print("Yo failed")
        assert False

    file = choices[int(inp)]
    filename = path + "/" + folder + "/" + file

    print("Chose", filename)

config = get_config_no_args()
folder = folder.replace("_", "-")
config.files.build_path = f"/Users/mia-katrinkvalsund/Desktop/Skole/master_project/Modbots/Modbots-master-{folder}.app"

side_channel = SideChannelPythonside()
param_channel = EnvironmentParametersChannel()

pid = os.getpid() % 10000 # Steinar fix

env = UnityEnvironment(
    file_name=config.files.build_path,
    seed = config.experiment.seed,
    side_channels=[side_channel, param_channel],
    no_graphics = config.experiment.headless,
    worker_id=pid,
    log_folder=config.files.log_folder
)
env.reset()

param_channel.set_float_parameter("torque", config.individual.torque)
param_channel.set_float_parameter("envEnum", config.evaluation.env_enum)

# Interesting ones: 601, 603, 606, 610, 618
# Attractive optima: 604, 605, 607, 608, 609, 611, 619, 620, 621, 623, 624, 627, 628
# Shambling messes: 612, 613, 614, 616, 617, 626, 629
# I think they're too light: 602, 615, 622

# 634, 637, 644, 646, 651, 654, 658
# Too powerful: 656

# 743 - 747
# My fave boy: 747
side_channel.send_string(f"Play,{filename}")

env.reset()

for i in range(config.evaluation.n_steps*2):
    env.step()

env.close()
