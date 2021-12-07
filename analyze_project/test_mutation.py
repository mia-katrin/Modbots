from config_util import get_config
from modbots.creature_types.configurable_individual import Individual

from tqdm import tqdm

config = get_config()

ind = Individual.random(config)

for i in range(100000):
    ind.needs_evaluation = False
    ind.prepare_for_evaluation()
    ind.mutate(config)
    if ind.needs_evaluation:
        print(f"{i}")
