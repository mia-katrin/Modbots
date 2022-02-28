import numpy as np
import copy

from modbots.util import traverse_get_list
from modbots.controllers.mutation_detection_ctrnn import add_count

class CopyDecentralController:
    def __init__(self, control_type, copies, body, **kwargs):
        self.kwargs = kwargs
        self.body = body
        cont = control_type()
        self.controller_clones = [cont]
        for _ in range(copies-1):
            self.controller_clones.append(copy.deepcopy(cont))
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
            if i < 50:
                actions[0,i] = cont.advance(observation[i*3:i*3+3], **self.kwargs)

        return actions

    def mutate_maybe(self, config):
        self._check_lack_of_control()

        mutation_story = ""

        allNodes = []
        traverse_get_list(self.body.root, allNodes)

        clone_shifts = 0
        # Mutate which controller each module uses
        if len(self.controller_clones) > 1:
            for node in allNodes:
                if np.random.rand() < config.mutation.switch_copy_likelihood*config.mutation.control:
                    possibilities = list(range(len(self.controller_clones)))

                    orig = node.clone_nr
                    possibilities.remove(orig)

                    node.clone_nr = np.random.choice(possibilities)

                    clone_shifts += 1

        if clone_shifts > 0:
            mutation_story = "Clone shifts: " + str(clone_shifts)

        # Keep track of which clones are actually used
        used_clones = []
        for node in allNodes:
            if node.clone_nr not in used_clones:
                used_clones.append(node.clone_nr)

        # Mutate controllers
        for i, cont in enumerate(self.controller_clones):
            if i in used_clones:
                res = cont.mutate_maybe(config, config.mutation.control)
                if res != None:
                    if mutation_story != "":
                        mutation_story += ", "
                    mutation_story += res

        return mutation_story if mutation_story != "" else None
