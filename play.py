from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel
import os

from modbots.evaluate.sideChannelPythonside import SideChannelPythonside

from config_util import get_config

config = get_config()

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

side_channel.send_string("Play,recorded_ind.txt")

env.reset()

for i in range(config.evaluation.n_steps):
    env.step()

env.close()
