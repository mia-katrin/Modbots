from colorama import Fore, Style

from modbots.evaluate import get_env, evaluate, close_env, set_env_variables
from modbots.creature_types.configurable_individual import Individual

from config_util import get_config_from_folder

path = "experiments/"

with open("runs500_folders_modes.txt", "r") as file:
    for line in file:
        line = line.replace("\n", "")
        run_folder = path + line

        config = get_config_from_folder(run_folder)
        ind = Individual.unpack_ind(run_folder + "/bestInd499", config)

        # Evaluate
        set_env_variables(config=config)

        fitness = evaluate(ind, force_evaluate=True, record=False)

        close_env()

        if fitness == ind.fitness:
            print(Fore.GREEN + "Fitness is fine")
        else:
            print(Fore.RED + "Fitness does not correspond")
