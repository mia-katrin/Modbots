import numpy as np
import pickle

from modbots.creature_types.body import Body
from modbots.controllers.decentral_controller import DecentralController
from modbots.controllers.sine_controller import SineController
from modbots.controllers.ctrnn_interface import CTRNNInterface
from modbots.controllers.copy_decentral import CopyDecentralController
from modbots.controllers.sensor_central import SensorCentral

class Individual:
    def __init__(self, config = None):
        if config != None:
            self.body = Body.random(config)
        self.fitness = -1
        self.needs_evaluation = True

        self.mutation_history = []

    indNr = 0
    @staticmethod
    def random(config):
        print(f"Creating ind nr {Individual.indNr}")
        Individual.indNr += 1
        self = Individual(config) # This gives me an interesting body

        # Select controller from config
        if config.control.oscillatory and not config.control.copy_decentral:
            print("Oscillatory decentral control chosen")
            self.controller = DecentralController(SineController, self.body, deltaTime=config.control.request_period)
        elif config.control.oscillatory and config.control.copy_decentral:
            print("Oscillatory decentral copy control chosen")
            self.controller = CopyDecentralController(SineController, self.body, deltaTime=config.control.request_period)
        elif config.control.ctrnn and config.control.copy_decentral:
            print("Ctrnn decentral copy control chosen")
            self.controller = CopyDecentralController(CTRNNInterface, self.body, advance_time=config.control.request_period, time_step=config.control.request_period)
        elif config.control.ctrnn and config.control.decentral:
            print("Ctrnn decentral control chosen")
            self.controller = DecentralController(CTRNNInterface, self.body, advance_time=config.control.request_period, time_step=config.control.request_period)
        elif config.control.ctrnn and config.control.pre_processing:
            print("Ctrnn preprocess central control chosen")
            self.controller = SensorCentral(self.body, advance_time=config.control.request_period, time_step=config.control.request_period)
        elif config.control.ctrnn:
            print("Ctrnn central control chosen")
            self.controller = CTRNNInterface(advance_time=config.control.request_period, config="45to15", time_step=config.control.request_period)
        else:
            self.controller = None
            print("You have chosen no controller")

        return self

    @staticmethod
    def unpack_ind(filename, config):
        with open(filename, 'rb') as file:
            self = pickle.load(file)

        return self

    def prepare_for_evaluation(self):
        if self.controller != None:
            self.controller.prepare_for_evaluation()

    def get_actions(self, observation):
        if self.controller != None:
            actions = self.controller.get_actions(observation)
            # Dead root
            actions[0][0] = 0.0
            return actions
        return np.zeros((1,50), dtype=float)

    def save_individual(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    def get_nr_modules(self) -> int:
        return self.body.get_nr_modules()

    def body_to_str(self):
        return self.body.to_str()

    def crossover(self, other) -> tuple:
        pass

    def mutate(self, config):
        if self.fitness >= 0:
            self.needs_evaluation = False

        result = ""
        if self.controller != None:
            if self.controller.mutate_maybe(config):
                result = "Control"

        result_body = self.body.mutate_maybe(config)
        if result_body != None:
            if result != "":
                result += ", "
            result += f"Body:{result_body}"

        if result != "":
            self.mutation_history.append(result)
            self.needs_evaluation = True

    def mutate2(self, config):
        if self.fitness >= 0:
            self.needs_evaluation = False

        rand_num = np.random.rand()
        if rand_num < config.ea.mut_rate*config.mutation.control and self.controller != None:
            self.controller.mutate(config) # Force mut if central else very likely but not always
            self.mutation_history.append("Control")
            mutated = True
        elif rand_num <= config.ea.mut_rate:
            mutated = self.body.mutate(config)
            self.mutation_history.append(f"Body:{self.body.mutation_history[-1]}")
        else:
            mutated = False

        if mutated:
            self.needs_evaluation = True
