import numpy as np
import copy

from modbots.util import traverse_get_list

class CopyDecentralController:
    def __init__(self, control_type, body, **kwargs):
        self.kwargs = kwargs
        self.body = body
        self.controller_clones = [control_type()]
        self.controllers = []

        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        for node in allNodes:
            node.clone_nr = 0

    def prepare_for_evaluation(self):
        self._check_lack_of_control()

        for cont in self.controller_clones:
            cont.reset()

        # Deepcopy controls
        self.controllers = []

        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        for node in allNodes:
            self.controllers.append(
                copy.deepcopy(
                    self.controller_clones[node.clone_nr]
                )
            )

    def _check_lack_of_control(self):
        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        for node in allNodes:
            if "clone_nr" not in node.__dict__.keys():
                print("This happened")

                parent = None
                for i in range(len(allNodes)-1, -1, -1):
                    if node in allNodes[i].children:
                        parent = allNodes[i]

                node.clone_nr = parent.clone_nr

    def get_actions(self, observation):
        actions = np.zeros((1,50), dtype=float)

        for i, cont in enumerate(self.controllers):
            actions[0,i] = cont.advance(observation[i*3:i*3+3], **self.kwargs)

        return actions

    def mutate(self, config):
        self._check_lack_of_control()

        # Chance of making new controller
        if len(self.controller_clones) < config.mutation.copy_number and np.random.rand() < config.mutation.copy_likelihood:
            self.controller_clones.append(
                copy.deepcopy(
                    np.random.choice(
                        self.controller_clones
                    )
                )
            )

        # Mutate which controller each module uses
        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        if len(self.controller_clones) > 1:
            for node in allNodes:
                if np.random.rand() < config.mutation.switch_copy_likelihood:
                    possibilities = list(range(len(self.controller_clones)))

                    orig = node.clone_nr
                    possibilities.remove(orig)

                    node.clone_nr = np.random.choice(possibilities)

        # Mutate controllers
        rand_nr = np.random.rand()
        for i, cont in enumerate(self.controller_clones):
            if rand_nr <= i / len(self.controller_clones):
                cont.mutate(config)
