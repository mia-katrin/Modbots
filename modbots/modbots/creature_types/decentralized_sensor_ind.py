import numpy as np

from modbots.controllers.neural_controller import NeuralController
from modbots.creature_types.abstract_individual import AbstractIndividual

class Individual(AbstractIndividual):
    def __init__(self, gene=None):
        super(Individual, self).__init__(controller_class=NeuralController)

    @staticmethod
    def random(depth):
        self = Individual()

        self = self.random_ind(depth, controller_class=NeuralController)

        return self

    def interpret_string_gene(self, gene):
        pass

    def get_actions(self, observation):
        actions = np.zeros(shape=(1,50),dtype=np.float32)

        allNodes = []
        self.traverse_get_list(self.bodyRoot, allNodes)

        for j, node in enumerate(allNodes):  # All controllers
            action = node.controller(observation[j*3:j*3+3])
            actions[0,j] = action

        return actions

    def prepare_for_evaluation(self):
        pass

    def ind_to_str(self):
        pass
