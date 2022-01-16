import numpy as np
import copy

from modbots.util import bounce_back, wrap_around

class Node:
    allowable_length = (0.1, 3)

    def __init__(self, variable_scale=False, growing=False):
        self.scale = .16 if growing else 1. if not variable_scale else np.random.rand() * 2. + .16
        self.angle = np.random.choice([0,90,180,270]).item() # to int
        self.children = [None,None,None]

    def mutate_angle(self, config) -> str:
        possibilities = [wrap_around(self.angle-90, [0, 270]), wrap_around(self.angle+90, [0, 270])]
        if not config.individual.growing:
            possibilities.append(self.angle+180 if self.angle < 180 else self.angle-180)

        old_angle = self.angle
        self.angle = np.random.choice(possibilities).item() # to int
        return f"Angle {self.angle - old_angle}"

    def mutate_remove(self, config) -> str:
        if config.individual.growing:
            leaves = self.get_indexes_of(lambda x: x is not None and x.is_leaf())
            if len(leaves) != 0:
                index = np.random.choice(leaves)
                if self.children[index].scale < 0.25:
                    self.children[index] = None
                    return "Remove dwarf"
                else:
                    val = self.children[index].scale - (np.random.rand()*0.2)
                    self.children[index].scale = max(val, self.allowable_length[0])
                    return "Remove shrink"
        else:
            occupied_spots = self.occupied_spots_list()
            if len(occupied_spots) > 0:
                self.children[np.random.choice(occupied_spots)] = None
                return "Remove full"
        return None

    def mutate_add_node(self, config) -> str:
        if config.individual.growing and self.scale < 1.0:
            val = self.scale + (np.random.rand()*0.2)
            self.scale = min(val, self.allowable_length[1])
            return "Add on grow"
        else:
            if len(self.open_spots_list()) > 0:
                new_node = Node(variable_scale=config.individual.variable_scale, growing=config.individual.growing)
                self.children[np.random.choice(self.open_spots_list())] = new_node
                return "Add on normal"
        return None

    def mutate_scale(self, config) -> str:
        if (config.individual.variable_scale or (config.individual.growing and self.scale < 1)):
            # growing and not variable
            if config.individual.growing and not config.individual.variable_scale:
                # Add a random small num
                val = self.scale + (np.random.rand() * 0.1)
                # Scale is that or 1, the smallest option
                self.scale = min(val, 1.0)
            else:
                # When growing and variable, or simply variable
                val = self.scale + (np.random.rand()*0.4 - 0.2)
                self.scale = bounce_back(val, self.allowable_length)

            if self.scale < 1.0:
                self.children[1] = None
                self.children[2] = None
            return f"Scale {val}"

        return None

    def mutate_copy_branch(self, config) -> str:
        occupied_spots = self.occupied_spots_list()
        if 1 <= len(occupied_spots) <= 2:
            child = self.children[np.random.choice(occupied_spots)]
            child = copy.deepcopy(child)
            self.children[np.random.choice(self.open_spots_list())] = child
            return "Copy"
        return None

    def _interval_func(self, so_far, mut_perc):
        func = lambda num: so_far <= num < so_far + mut_perc
        return func, so_far+mut_perc

    def mutate(self, config):
        so_far = 0
        within_angle,       so_far = self._interval_func(so_far, config.mutation.angle)
        within_remove,      so_far = self._interval_func(so_far, config.mutation.remove_node)
        within_add_node,    so_far = self._interval_func(so_far, config.mutation.add_node)
        within_scale,       so_far = self._interval_func(so_far, config.mutation.scale)
        within_copy_branch, so_far = self._interval_func(so_far, config.mutation.copy_branch)

        for _ in range(100):
            rand_num = np.random.rand()
            result = None

            for mut_type in ["angle", "remove", "add_node", "scale", "copy_branch"]:
                within_func = eval(f"within_{mut_type}")
                mutate_func = eval(f"self.mutate_{mut_type}")

                if within_func(rand_num):
                    result = mutate_func(config)

                if result != None:
                    return result

        print("Could not mutate!")
        return "None"

    def open_spots_list(self):
        return self.get_indexes_of(lambda x: x is None)

    def occupied_spots_list(self):
        return self.get_indexes_of(lambda x: x is not None)

    def get_indexes_of(self, expression):
        """NB: Can throw AttributeError if you do not check position isn't None"""
        indexes = []
        for i in range(len(self.children)):
            if expression(self.children[i]):
                indexes.append(i)
        return indexes

    def is_leaf(self):
        return len(self.occupied_spots_list()) == 0
