import numpy as np
import json

from modbots.controllers.neural_controller import NeuralController
from modbots.creature_types.abstract_individual import AbstractIndividual

from modbots.creature_types.node import Node

class Individual(AbstractIndividual):
    def __init__(self, gene=None):
        super(Individual, self).__init__(controller_class=NeuralController, gene=gene)

    @staticmethod
    def random(depth):
        self = Individual()

        self = self.random_ind(depth, controller_class=NeuralController)

        return self

    def interpret_string_gene(self, gene):
        parts = gene.split("\n")

        self.interpret_body_string(parts[0])

        allNodes = []
        self.traverse_get_list(self.bodyRoot, allNodes)

        for controller, module in zip(parts[1:], allNodes):
            module.controller = NeuralController.build_from_string(controller)

    def interpret_body_string(self, gene):
        gene = np.array(gene.split("|"))
        root_info = np.array(gene[0].split(",")).astype(float)
        self.bodyRoot.scale = root_info[0]

        pretend_stack = []
        node = self.bodyRoot

        for info in gene:
            if info == "":
                pass
            elif info[0] == "M":
                # Construct module
                child_info = np.array(info[1:].split(",")).astype(float)
                child = Node()
                node.children[int(child_info[0])] = child

                child.angle = int(child_info[1])
                child.scale = child_info[2]

                node = child

            elif info[0] == "[":
                # node on stack
                pretend_stack.append(node)
            elif info[0] == "]":
                # Node off stack
                node = pretend_stack.pop()

    def get_actions(self, observation):
        actions = np.zeros(shape=(1,50),dtype=np.float32)

        allNodes = []
        self.traverse_get_list(self.bodyRoot, allNodes)

        for j, node in enumerate(allNodes):  # All controllers
            o = observation[j*3:j*3+3]
            for i in range(3):
                if o[i] == -1:
                    o[i] = 100
            action = node.controller(o)
            actions[0,j] = action

        return actions

    def prepare_for_evaluation(self):
        pass

    def ind_to_str(self):
        ind = self.body_to_str()

        allNodes = []
        self.traverse_get_list(self.bodyRoot, allNodes)

        for node in allNodes:
            ind += "\n" + node.controller.info_to_str()

        return ind
