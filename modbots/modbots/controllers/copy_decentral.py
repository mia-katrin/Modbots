import numpy as np
import copy

from modbots.util import traverse_get_list

class CopyDecentralController:
    def __init__(self, control_type, body, **kwargs):
        self.kwargs = kwargs
        self.body = body
        self.controller = control_type()
        self.controllers = []

    def prepare_for_evaluation(self):
        self.controller.reset()

        # Deepcopy controls
        self.controllers = []

        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        for node in allNodes:
            self.controllers.append(copy.deepcopy(self.controller))

    def get_actions(self, observation):
        actions = np.zeros((1,50), dtype=float)

        for i, cont in enumerate(self.controllers):
            actions[0,i] = cont.advance(observation[i*3:i*3+3], **self.kwargs)

        return actions

    def mutate(self):
        self.controller.mutate()
