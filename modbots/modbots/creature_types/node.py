import numpy as np
import copy

from modbots.util import bounce_back, wrap_around


class Node:
    def __init__(self, variable_scale=False, growing=False):
        self.scale = .16 if growing else 1. if not variable_scale else np.random.rand() * 2. + .16
        self.angle = np.random.choice([0,90,180,270]).item() # to int
        self.children = [None,None,None]

    def mutate(self, config):
        for _ in range(100):
            rand_num = np.random.rand()

            # Angle
            if rand_num < config.mutation.angle:
                change = -90 if np.random.rand() <= 0.5 else 90
                self.angle += change
                self.angle = wrap_around(self.angle, [0, 270])
                return f"Angle {change}"
            # Remove node
            elif rand_num < config.mutation.angle + config.mutation.remove_node:
                leaves = self.get_indexes_of(lambda x: x is not None and x.isleaf())
                if len(leaves) != 0:
                    self.children[np.random.choice(leaves)] = None
                    return "Remove"
            # Add node
            elif rand_num < config.mutation.angle + config.mutation.remove_node + config.mutation.add_node:
                if self.scale < 1. and self.children[0] == None:
                    new_node = Node(variable_scale=config.individual.variable_scale, growing=config.individual.growing)
                    self.children[0] = new_node
                    return "Add on dwarf"
                elif self.scale >= 1. and len(self.open_spots_list()) != 0:
                    new_node = Node(variable_scale=config.individual.variable_scale, growing=config.individual.growing)
                    self.children[np.random.choice(self.open_spots_list())] = new_node
                    return "Add on normal"
            # Scale
            # elif ((growing and short) or variable) and rand_num
            elif ((config.individual.growing and self.scale < 1) or config.individual.variable_scale) and rand_num < config.mutation.angle + config.mutation.remove_node + config.mutation.add_node + config.mutation.scale:
                # growing and not variable
                if config.individual.growing and not config.individual.variable_scale:
                    # Add a random small num
                    val = self.scale + (np.random.rand() * 0.1)
                    # Scale is that or 1, the smallest option
                    self.scale = min(val, 1)
                else:
                    # When growing and variable, or simply variable
                    val = self.scale + (np.random.rand()*0.2 - 0.1)
                    self.scale = bounce_back(val, (0.1, 3))

                if self.scale < 1.0:
                    self.children[1] = None
                    self.children[2] = None
                return f"Scale {val}"
            # Copy branch
            elif rand_num <= config.mutation.angle + config.mutation.remove_node + config.mutation.add_node + config.mutation.scale + config.mutation.copy_branch:
                if 1 <= len(self.occupied_spots_list()) <= 2:
                    child = self.children[np.random.choice(self.occupied_spots_list())]
                    child = copy.deepcopy(child)
                    self.children[np.random.choice(self.open_spots_list())] = child
                    return "Copy"

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

    def isleaf(self):
        return len(self.occupied_spots_list()) == 0
