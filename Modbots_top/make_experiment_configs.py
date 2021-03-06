from config_util import get_local_config

with open("experiments/max_cores.txt") as file:
    n_cores = int(file.read())

import argparse
parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='Default config get parser')
parser.add_argument(
    '--config_file',
    type = str,
    help='The config file to configure this evolution',
    default=get_local_config()
)
parser.add_argument("--mode", "-m", type=str)
parser.add_argument("--brain", "-br", type=str)
parser.add_argument("--cs", "-c", nargs='+', required=True)
parser.add_argument("--bs", "-b", nargs='+', required=True)
parser.add_argument(
    '--final', '-f',
    action="store_true",
    help='Final run? Yields different config name and generations',
    default=False
)

args = parser.parse_args()
from localconfig import config
config.read(args.config_file)

mode = args.mode if args.mode != "normal" else ""
brain = args.brain if args.brain != "sine" else ""

cs = [float(i) for i in args.cs]
bs = [float(i) for i in args.bs]

final = args.final

########## Config Make ##########

# EXPERIMENT
config.experiment.seed = 1
config.experiment.documentation = True # Must always be True
config.experiment.n_cores = n_cores
config.experiment.headless = True # Must always be True

# EA
config.ea.mut_rate = 1.0
if brain == "":
    config.ea.control_sigma = 0.5
else:
    config.ea.control_sigma = 0.2
config.ea.body_sigma = 0.5
if final:
    config.ea.n_generations = 500
else:
    config.ea.n_generations = 50
pop_size = 50
config.ea.pop_size = n_cores*(pop_size//n_cores + (1 if pop_size%n_cores!=0 else 0))
config.ea.nr_parents = 0
config.ea.tournsize = 4

# INDIVIDUAL
config.individual.torque = 0.0
config.individual.ind_depth = 5
config.individual.force_interesting = True
config.individual.creation_mu = 0.75
config.individual.creation_std = 0.35

config.individual.variable_scale = False
config.individual.growing = False
config.individual.gradual = False
if mode != "":
    config.individual.variable_scale = True
    if mode != "variable":
        config.individual.growing = True
        if mode != "growing":
            config.individual.gradual = True

# EVALUATION
config.evaluation.n_steps = 100
config.evaluation.n_start_eval = 10
config.evaluation.time_scale = None
config.evaluation.env_enum = 0.0

# CONTROL
config.control.oscillatory = False
config.control.ctrnn = False
config.control.decentral = False
config.control.copy_decentral = False
config.control.pre_processing = False
if brain == "":
    config.control.oscillatory = True
    config.control.decentral = True
elif brain == "copy":
    config.control.ctrnn = True
    config.control.decentral = True
    config.control.copy_decentral = True
elif brain == "dec_ctrnn":
    config.control.ctrnn = True
    config.control.decentral = True
elif brain == "copy_sine":
    config.control.ctrnn = True
    config.control.decentral = True
    config.control.copy_decentral = True
elif brain == "dec_ctrnn_sine":
    config.control.ctrnn = True
    config.control.decentral = True
elif brain == "cen_ctrnn":
    config.control.ctrnn = True
else:
    assert False

config.control.request_period = 0.2
# Copy brain mutation
config.mutation.copy_number = 2
config.mutation.switch_copy_likelihood = 1.0

# MUTATION
if mode == "":
    # With no scale
    config.mutation.angle = 0.2
    config.mutation.remove_node = 0.25
    config.mutation.add_node = 0.3
    config.mutation.scale = 0.0
    config.mutation.copy_branch = 0.25
else:
    # With scale
    config.mutation.angle = 0.15
    config.mutation.remove_node = 0.2
    config.mutation.add_node = 0.25
    config.mutation.scale = 0.2
    config.mutation.copy_branch = 0.2

# Files remains as default on computer

# MUTATION

if brain != "":
    brain = "_" + brain
for c, b in zip(cs, bs):
    config.mutation.control = c
    config.mutation.body = b
    if final:
        if mode != "":
            mode = "_" + mode
        config.save(f"final{mode}{brain}.cfg")
        print("Made", f"final{mode}{brain}.cfg")
    else:
        c = str(c)[2:]
        b = str(b)[2:]
        config.save(f"0{c}c0{b}b{mode}{brain}.cfg")
        print("Made", f"0{c}c0{b}b{mode}{brain}.cfg")
