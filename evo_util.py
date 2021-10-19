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

    return sorted
