"""Abstract methods that are rquired by evaluate and evolve"""

from abc import ABC, abstractmethod
from modbots.creature_types.node import Node

class AbstractIndividual:
    def __init__(self, gene=None):
        self.bodyRoot = Node()
        self.fitness = -1
        self.needs_evaluation = True
        self._nr_expressed_modules = -1
        if gene is not None:
            self.interpret_string_gene(gene)

    @staticmethod
    @abstractmethod
    def random(depth):
        pass

    @abstractmethod
    def interpret_string_gene(self, gene):
        pass

    @abstractmethod
    def get_actions(self, observation):
        pass

    @abstractmethod
    def prepare_for_evaluation(self):
        pass

    @abstractmethod
    def get_nr_modules(self):
        pass

    @abstractmethod
    def body_to_str(self):
        pass

    @abstractmethod
    def crossover(self):
        pass

    @abstractmethod
    def mutate(self):
        pass
