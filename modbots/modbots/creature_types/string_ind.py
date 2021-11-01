import copy
import numpy as np

from modbots.creature_types.node import Node
from modbots.util import bool_from_distribution
from modbots.controllers.sine_controller import Controller

from modbots.creature_types.abstract_individual import AbstractIndividual

class Individual(AbstractIndividual):
    def __init__(self, gene=None):
        super(Individual, self).__init__(controller_class=Controller)

    @staticmethod
    def random(depth):
        self = Individual()

        self.random_ind(depth, controller_class=Controller)

        return self

    def interpret_string_gene(self, gene):
        gene = np.array(gene.split("|"))
        root_info = np.array(gene[0].split(",")).astype(float)
        self.bodyRoot.scale = root_info[0]
        self.bodyRoot.controller.amp = root_info[1]
        self.bodyRoot.controller.freq = root_info[2]
        self.bodyRoot.controller.phase = root_info[3]
        self.bodyRoot.controller.offset = root_info[4]

        pretend_stack = []
        node = self.bodyRoot

        for info in gene:
            if info == "":
                pass
            elif info[0] == "M":
                # Construct module
                child_info = np.array(info[1:].split(",")).astype(float)
                child = Node(controller=Controller())
                node.children[int(child_info[0])] = child

                child.angle = int(child_info[1])
                child.scale = child_info[2]
                child.controller.amp = child_info[3]
                child.controller.freq = child_info[4]
                child.controller.phase = child_info[5]
                child.controller.offset = child_info[6]

                node = child

            elif info[0] == "[":
                # node on stack
                pretend_stack.append(node)
            elif info[0] == "]":
                # Node off stack
                node = pretend_stack.pop()

    def prepare_for_evaluation(self):
        allNodes = []
        self.traverse_get_list(self.bodyRoot, allNodes)

        # Ensure all controllers are reset
        for node in allNodes:  # All controllers
            node.controller.reset()

    def get_actions(self, observation):
        actions = np.zeros(shape=(1,50),dtype=np.float32)

        allNodes = []
        self.traverse_get_list(self.bodyRoot, allNodes)

        for j, node in enumerate(allNodes):  # All controllers
            action = node.controller.update(0.05)
            actions[0,j] = action

        return actions

    def ind_to_str(self):
        return self.to_str(with_control=True)
