from modbots.util import *
from config_util import get_config

def calc_time():
    config = get_config()
    seconds = calc_time_evolution(config)
    minutes = seconds / 60
    hours = minutes / 60
    return hours

def calc_all(runs):
    time = 0
    for _ in range(runs):
        time += calc_time()
    return time

print(calc_all(20)*12/24)
