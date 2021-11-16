import numpy as np

from modbots.util import bounce_back, wrap_around

class Node:
    def __init__(self, variable_scale=False, growing=False):
        self.scale = .1 if growing else 1. if not variable_scale else np.random.rand() * 2. + 1.
        self.angle = np.random.choice([0,90,180,270]).item() # to int
        self.children = [None,None,None]

    def mutate(self, config):
        for _ in range(1000):
            rand_num = np.random.rand()

            # Angle
            if rand_num < config.mutation.angle:
                self.angle += -90 if np.random.rand() <= 0.5 else 90
                self.angle = wrap_around(self.angle, [0, 270])
                return
            # Remove node
            elif rand_num < config.mutation.angle + config.mutation.remove_node:
                if len(self.occupied_spots_list()) != 0:
                    self.children[np.random.choice(self.occupied_spots_list())] = None
                    return
            # Add node
            elif rand_num < config.mutation.angle + config.mutation.remove_node + config.mutation.add_node:
                if len(self.open_spots_list()) != 0:
                    new_node = Node(variable_scale=config.individual.variable_scale, growing=config.individual.growing)
                    self.children[np.random.choice(self.open_spots_list())] = new_node
                    return
            # Scale
            elif rand_num < config.mutation.angle + config.mutation.remove_node + config.mutation.add_node + config.mutation.scale:
                val = self.scale + (np.random.rand() - 0.5)
                self.scale = bounce_back(val, (0.1, 3))
                return
            # Copy branch
            elif rand_num <= config.mutation.angle + config.mutation.remove_node + config.mutation.add_node + config.mutation.scale + config.mutation.copy_branch:
                pass
            else:
                print("Oh no!")

        print("Could not mutate!") # Should never really happen

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
