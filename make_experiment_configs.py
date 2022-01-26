from config_util import get_config

config = get_config()

with open("experiments/max_cores.txt") as file:
    n_cores = int(file.read())

# EXPERIMENT
config.experiment.seed = 1
config.experiment.documentation = True # Must always be True
config.experiment.n_cores = 100
config.experiment.headless = True # Must always be True

# EA
config.ea.mut_rate = 1.00
config.ea.control_sigma = 0.05
config.ea.body_sigma = 0.05
config.ea.n_generations = 100
pop_size = 100
config.ea.pop_size = n_cores*(pop_size//n_cores + (1 if pop_size%n_cores!=0 else 0))
config.ea.nr_parents = 0
config.ea.tournsize = 4

# INDIVIDUAL
config.individual.torque = 0.0
config.individual.ind_depth = 5
config.individual.force_interesting = True
config.individual.creation_mu = 0.75
config.individual.creation_std = 0.35

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
config.mutation.control = 0.4
config.mutation.body = 0.6

# Files remains as default on computer

# MUTATION + INDIVIDUAL
# Case 1
config.individual.variable_scale = False
config.individual.growing = False
config.individual.gradual = False

config.mutation.angle = 0.15
config.mutation.remove_node = 0.25
config.mutation.add_node = 0.3
config.mutation.scale = 0.0
config.mutation.copy_branch = 0.3

config.save("baseline.cfg")

# Case 2
config.individual.variable_scale = True
config.individual.growing = False
config.individual.gradual = False

config.mutation.angle = 0.1
config.mutation.remove_node = 0.2
config.mutation.add_node = 0.25
config.mutation.scale = 0.25
config.mutation.copy_branch = 0.2

config.save("variable_scale.cfg")

# Case 3
config.individual.variable_scale = True
config.individual.growing = True
config.individual.gradual = False

config.mutation.angle = 0.1
config.mutation.remove_node = 0.2
config.mutation.add_node = 0.25
config.mutation.scale = 0.25
config.mutation.copy_branch = 0.2

config.save("growing.cfg")

# Case 4
config.individual.variable_scale = True
config.individual.growing = True
config.individual.gradual = True

config.mutation.angle = 0.1
config.mutation.remove_node = 0.2
config.mutation.add_node = 0.25
config.mutation.scale = 0.25
config.mutation.copy_branch = 0.2

config.save("gradual.cfg")
