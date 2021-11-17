import numpy as np
import pickle

from modbots.creature_types.body import Body
from modbots.controllers.decentral_controller import DecentralController
from modbots.controllers.sine_controller import SineController
from modbots.controllers.ctrnn_interface import CTRNNInterface

class Individual:
    def __init__(self, config = None):
        if config != None:
            self.body = Body.random(config)
        self.fitness = -1
        self.needs_evaluation = True

    @staticmethod
    def random(config):
        self = Individual(config) # This gives me an interesting body

        # Select controller from config
        if config.control.oscillatory:
            self.controller = DecentralController(SineController, self.body, deltaTime=0.1)
        elif config.control.ctrnn and config.control.decentral:
            self.controller = DecentralController(CTRNNInterface, self.body, advance_time=0.02, time_step=0.02)
        elif config.control.ctrnn:
            self.controller = CTRNNInterface(advance_time=0.02, central=True, time_step=0.02)
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
            return self.controller.get_actions(observation)
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

        rand_num = np.random.rand()
        if rand_num < config.ea.mut_rate*config.mutation.control and self.controller != None:
            self.controller.mutate() # Force mut if central else very likely but not always
            mutated = True
        elif rand_num < config.ea.mut_rate:
            mutated = self.body.mutate(config)
        else:
            mutated = False

        if mutated:
            self.needs_evaluation = True
