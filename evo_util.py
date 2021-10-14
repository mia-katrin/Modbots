def bounce_back(value, allowable_range):
    if value < allowable_range[0]:
        return value + 2*(allowable_range[0] - value)
    elif value > allowable_range[1]:
        return value - 2*(value - allowable_range[1])
    return value

def wrap_around(value, allowable_range):
    if value < allowable_range[0]:
        return allowable_range[1]
    elif value > allowable_range[1]:
        return allowable_range[0]
    return value
