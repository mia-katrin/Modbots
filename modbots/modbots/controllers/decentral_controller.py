import numpy as np
import copy

from modbots.util import traverse_get_list

class DecentralController:
    def __init__(self, control_type, body, **kwargs):
        self.kwargs = kwargs
        self.body = body
        self.control_type = control_type

        allNodes = []
        traverse_get_list(body.root, allNodes)

        for node in allNodes:
            node.controller = control_type()

    def prepare_for_evaluation(self):
        # If mutation addition occured, we're lacking a controller
        self._check_lack_of_control()

        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        for node in allNodes:
            node.controller.reset()

    def _check_lack_of_control(self):
        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        for node in allNodes:
            if "controller" not in node.__dict__.keys():
                print("This happened")

                parent = None
                for i in range(len(allNodes)-1, -1, -1):
                    if node in allNodes[i].children:
                        parent = allNodes[i]

                node.controller = copy.deepcopy(parent.controller)

    def get_actions(self, observation):
        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        actions = np.zeros((1,50), dtype=float)

        for i, node in enumerate(allNodes):
            if i < 50:
                actions[0,i] = node.controller.advance(observation[i*3:i*3+3], **self.kwargs)

        return actions

    def mutate_maybe(self, config):
        self._check_lack_of_control()

        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        individual_likelihood = config.mutation.control/len(allNodes)

        mutated = False
        for node in allNodes:
            if node != self.body.root:
                # Lazy execution, hence always call mutate alone
                res = node.controller.mutate_maybe(config, individual_likelihood)
                mutated = mutated or res

        return mutated

    def mutate(self, config):
        self._check_lack_of_control()

        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        individual_likelihood = 1/len(allNodes)

        mutated = False
        for node in allNodes:
            if np.random.rand() < individual_likelihood and node.scale >= 1.0:
                node.controller.mutate(config)
                mutated = True

        if not mutated:
            self.mutate(config)
