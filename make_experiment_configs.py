from config_util import get_config

config = get_config()

with open("experiments/max_cores.txt") as file:
    n_cores = int(file.read())

# EXPERIMENT
config.experiment.seed = 1
config.experiment.documentation = True # Must always be True
config.experiment.n_cores = n_cores
config.experiment.headless = True # Must always be True

# EA
config.ea.mut_rate = 1.0
config.ea.control_sigma = 0.5
config.ea.body_sigma = 0.5
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

config.individual.variable_scale = True
config.individual.growing = False
config.individual.gradual = False

# EVALUATION
config.evaluation.n_steps = 100
config.evaluation.n_start_eval = 10
config.evaluation.time_scale = None
config.evaluation.env_enum = 0.0

# CONTROL
config.control.oscillatory = True
config.control.ctrnn = False
config.control.decentral = True
config.control.copy_decentral = False
config.control.pre_processing = False

config.control.request_period = 0.2

# MUTATION
# With no scale
#config.mutation.angle = 0.2
#config.mutation.remove_node = 0.25
#config.mutation.add_node = 0.3
#config.mutation.scale = 0.0
#config.mutation.copy_branch = 0.25

# With scale
config.mutation.angle = 0.15
config.mutation.remove_node = 0.2
config.mutation.add_node = 0.25
config.mutation.scale = 0.2
config.mutation.copy_branch = 0.2

# Files remains as default on computer

# MUTATION

# Case 1
config.mutation.control = 0.64
config.mutation.body = 0.32
config.save("064c032bvariable.cfg")

# Case 2
config.mutation.control = 0.64
config.mutation.body = 0.48
config.save("064c048bvariable.cfg")

# Case 3
config.mutation.control = 0.64
config.mutation.body = 0.82
config.save("064c082bvariable.cfg")

# Case 4
config.mutation.control = 0.32
config.mutation.body = 0.64
config.save("032c064bvariable.cfg")

# Case 5
config.mutation.control = 0.48
config.mutation.body = 0.64
config.save("048c064bvariable.cfg")

# Case 6
config.mutation.control = 0.82
config.mutation.body = 0.64
config.save("082c064bvariable.cfg")

# Case 7
config.mutation.control = 0.48
config.mutation.body = 0.32
config.save("048c032bvariable.cfg")

# Case 8
config.mutation.control = 0.32
config.mutation.body = 0.48
config.save("032c048bvariable.cfg")
