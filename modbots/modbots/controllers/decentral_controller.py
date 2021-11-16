import numpy as np

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
                node.controller = self.control_type()

    def get_actions(self, observation):
        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        actions = np.zeros((1,50), dtype=float)

        for i, node in enumerate(allNodes):
            actions[0,i] = node.controller.advance(observation[i*3:i*3+3], **self.kwargs)

        return actions

    def mutate(self):
        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        individual_likelihood = 1/len(allNodes)

        for node in allNodes:
            if np.random.rand() < individual_likelihood:
                node.controller.mutate()
