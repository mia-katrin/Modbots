import numpy as np

def calc_time_evolution(pop_size, n_cores, mut_rate, nr_parents, n_steps, n_gen, time_scale=None):
    avg_one_ind_time = n_steps*0.02/(n_cores * (time_scale if time_scale != None else 1))

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
