import numpy as np

def traverse_get_list(node, node_list_out):
    node_list_out.append(node)

    for child in node.children:
        if child is not None:
            traverse_get_list(child, node_list_out)

def calc_time_evolution(config):
    pop_size = config.ea.pop_size
    n_cores = config.experiment.n_cores 
    mut_rate = config.ea.mut_rate
    nr_parents = config.ea.nr_parents
    n_steps = config.evaluation.n_steps
    n_gen = config.ea.n_generations
    time_scale = config.evaluation.time_scale

    avg_one_ind_time = n_steps*0.2/(n_cores * (time_scale if time_scale != None else 1))

    round0 = pop_size*avg_one_ind_time
    inds_geni = (pop_size*mut_rate)+nr_parents
    roundi = inds_geni*avg_one_ind_time

    all_gen = roundi*n_gen

    return all_gen + round0

def bounce_back(value, allowable_range):
    if value < allowable_range[0]:
        if value + 2*(allowable_range[0] - value) > allowable_range[1]:
            raise ValueError
        return value + 2*(allowable_range[0] - value)
    elif value > allowable_range[1]:
        if value - 2*(value - allowable_range[1]) < allowable_range[0]:
            raise ValueError
        return value - 2*(value - allowable_range[1])
    return value

def wrap_around(value, allowable_range):
    if value < allowable_range[0]:
        return allowable_range[1]
    elif value > allowable_range[1]:
        return allowable_range[0]
    return value

def sort_to_chunks(offspring, nr_chunks):
    cs = len(offspring) // nr_chunks

    sorted = [None]*len(offspring)
    indexes = [[i*cs, (i+1)*cs-1] for i in range(nr_chunks)]

    mutated = []
    normal = []

    for o in offspring:
        if o.needs_evaluation:
            mutated.append(o)
        else:
            normal.append(o)

    chunk = 0
    for m in mutated:
        sorted[indexes[chunk][0]] = m
        indexes[chunk][0] += 1
        chunk = chunk+1 if chunk+1 < nr_chunks else 0

    chunk = nr_chunks-1
    for n in normal:
        sorted[indexes[chunk][1]] = n
        indexes[chunk][1] -= 1
        chunk = chunk-1 if chunk-1 >= 0 else nr_chunks-1

    assert np.all(sorted != None), "Sorting has failed"

    return sorted

def bool_from_distribution(type, threshold=None, c_mu=None, c_std=None, depth=None, o_depth=None):
    if type == "gaussian":
        return np.random.normal(c_mu, c_std) < depth/o_depth
    elif type == "uniform":
        return np.random.rand() < threshold
    else:
        raise ValueError("You've not stated the type of distribution!")

def rotx(theta):
    t = theta*np.pi/180
    return np.array([
        [1, 0, 0, 0],
        [0, np.cos(t),-np.sin(t), 0],
        [0, np.sin(t), np.cos(t), 0],
        [0, 0, 0, 1]
    ]).astype(int)

def roty(theta):
    t = theta*np.pi/180
    return np.array([
        [np.cos(t), 0, -np.sin(t), 0],
        [0, 1, 0, 0],
        [np.sin(t), 0, np.cos(t), 0],
        [0, 0, 0, 1]
    ]).astype(int)

def rotz(theta):
    t = theta*np.pi/180
    return np.array([
        [np.cos(t),-np.sin(t), 0, 0],
        [np.sin(t), np.cos(t), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]).astype(int)
