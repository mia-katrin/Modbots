from abc import ABC, abstractmethod

class Individual:
    def __init__(self, gene=None):
        self.bodyRoot = Node()
        self.fitness = -1
        self.needs_evaluation = True
        self._nr_expressed_modules = -1
        if gene is not None:
            self.interpret_string_gene(gene)

    @abstractmethod
    def interpret_string_gene(self, gene):
        pass

    @abstractmethod
    def get_actions(self, observation):
        pass
