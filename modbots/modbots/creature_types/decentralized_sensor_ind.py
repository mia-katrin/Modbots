from modbots.controllers.neural_controller import NeuralController

class Individual(AbstractIndividual):
    def __init__(self, gene=None):
        super(Individual, self).__init__(controller_class=NeuralController)

    @staticmethod
    def random(depth):
        self = Individual()

        self.random_ind(depth, controller_class=NeuralController)

        return self

    def interpret_string_gene(self, gene):
        pass

    def get_actions(self, observation):
        pass

    def prepare_for_evaluation(self):
        pass

    def ind_to_str(self):
        pass
