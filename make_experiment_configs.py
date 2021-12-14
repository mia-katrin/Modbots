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
config.ea.mut_rate = 0.1
config.ea.n_generations = 100
config.ea.pop_size = 100
config.ea.nr_parents = 0
config.ea.tournsize = 2

# INDIVIDUAL
config.individual.ind_depth = 5
config.individual.creation_mu = 0.75
config.individual.creation_std = 0.35

# EVALUATION
config.evaluation.n_steps = 100
config.evaluation.n_start_eval = 10
config.evaluation.time_scale = None

# Files remains as default on computer

# CONTROL + INDIVIDUAL
config.individual.torque = 1.0

for control in ["sine", "ctrnn", "decentral_ctrnn", "copy_ctrnn", "pre_ctrnn"]:
    config.control.oscillatory = True if control == "sine" else False
    config.control.ctrnn = True if not control == "sine" else False
    config.control.decentral = True if not control == "ctrnn" and not control == "pre_ctrnn" else False
    config.control.copy_decentral = True if control == "copy_ctrnn" else False
    config.control.pre_processing = True if control == "pre_ctrnn" else False

    if control == "copy_ctrnn":
        # Copy brain mutation
        config.mutation.copy_number = 2
        config.mutation.copy_likelihood = 0.5
        config.mutation.switch_copy_likelihood = 0.05

    if control == "pre_ctrnn":
        # Copy brain mutation
        config.mutation.copy_number = 1
        config.mutation.copy_likelihood = 0.0
        config.mutation.switch_copy_likelihood = 0.00

    # MUTATION + INDIVIDUAL
    for mode in ["", "_growing"]:
        if mode == "_growing":
            config.mutation.control = 0.5
            config.mutation.body = 0.5
            config.mutation.angle = 0.1
            config.mutation.remove_node = 0.3
            config.mutation.add_node = 0.4
            config.mutation.scale = 0.2

            config.individual.variable_scale = True
            config.individual.growing = True
        else:
            config.mutation.control = 0.5
            config.mutation.body = 0.5
            config.mutation.angle = 0.2
            config.mutation.remove_node = 0.3
            config.mutation.add_node = 0.5
            config.mutation.scale = 0.0

            config.individual.variable_scale = False
            config.individual.growing = False

        config.save(control + mode + ".cfg")
