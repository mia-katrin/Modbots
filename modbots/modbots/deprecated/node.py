import numpy as np

from modbots.util import bounce_back, wrap_around

class Node:
    def __init__(self, init_mode="random", controller=None):
        if init_mode == "empty":
            self.scale = 1.0
            self.angle = 0
        elif init_mode == "dwarf":
            self.scale = 0.1
            self.controller = controller
            self.controller.amp = 0.0
            self.controller.freq = 0.0
            self.controller.phase = 0.0
            self.controller.offset = 0.0
            self.angle = np.random.choice([0,90,180,270]).item() # to int
        elif init_mode == "random":
            self.angle = np.random.choice([0,90,180,270]).item() # to int
            self.scale = 1.0#np.random.rand() * 2. + 1.
            self.controller = controller
        else:
            raise ValueError("No other mode supported")
        self.children = [None,None,None]

    def mutate_breadth(self, mutation_rate):
        mutated = False

        current_nodes = [self]

        while len(current_nodes) > 0:
            node = current_nodes.pop(0)

            if np.random.rand() < mutation_rate:
                mutated = True
                node.mutate()

            for child in node.children:
                if child != None:
                    current_nodes.append(child)

        return mutated

    def mutate(self):
        mutated = False
        while not mutated:
            rand_num = np.random.rand()

            if is_in(INTERVALS["control"], rand_num) and self.controller is not None:
                self.controller.mutate()
                mutated = True
            elif is_in(INTERVALS["angle"], rand_num):
                self.angle += -90 if np.random.rand() <= 0.5 else 90
                self.angle = wrap_around(self.angle, [0, 270])
                mutated = True
            elif is_in(INTERVALS["remove_node"], rand_num):
                if len(self.occupied_spots_list()) != 0:
                    self.children[np.random.choice(self.occupied_spots_list())] = None
                    mutated = True
            elif is_in(INTERVALS["add_node"], rand_num):
                if len(self.open_spots_list()) != 0:
                    new_node = Node(controller=type(self.controller)())
                    self.children[np.random.choice(self.open_spots_list())] = new_node
                    mutated = True
            elif is_in(INTERVALS["scale"], rand_num):
                val = self.scale + (np.random.rand() - 0.5)
                self.scale = bounce_back(val, (0.1, 3))
                mutated = True
            elif is_in(INTERVALS["copy_branch"], rand_num):
                pass

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
        for child in self.children:
            if child is not None:
                return False
        return True
