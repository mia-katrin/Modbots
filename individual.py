from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.side_channel import (
    SideChannel,
    IncomingMessage,
    OutgoingMessage,
)
import numpy as np
import uuid
import os
from random import shuffle

from custom_controller import Controller
from evo_util import bounce_back

CREATION_MU = 0.75 # Higher means fewer average modules
CREATION_STD = 0.35 # Higher means more variance in number of modules

class Node:
    def __init__(self):
        self.children = [None,None,None]
        self.angle = np.random.choice([0,90,180,270])
        self.scale = np.random.rand() * 2.9 + 0.1
        self.controller = Controller("Hei :)") # Not unique hash because I don't use it yet

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

class Individual:
    def __init__(self, gene=None):
        self.genomeRoot = Node()
        self.fitness = 0
        self.needs_evaluation = True
        self._nr_expressed_modules = -1
        if gene is not None:
            gene = np.array(gene.split("|"))
            root_info = np.array(gene[0].split(",")).astype(float)
            self.genomeRoot.scale = root_info[0]
            self.genomeRoot.controller.amp = root_info[1]
            self.genomeRoot.controller.freq = root_info[2]
            self.genomeRoot.controller.phase = root_info[3]
            self.genomeRoot.controller.offset = root_info[4]
            self.interpret_string_gene(gene)

    def interpret_string_gene(self, gene):
        pretend_stack = []
        node = self.genomeRoot

        for info in gene:
            if info == "":
                print("Found empty string")
            elif info[0] == "M":
                # Construct module
                child_info = np.array(info[1:].split(",")).astype(float)
                child = Node()
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

    @staticmethod
    def random(depth):
        self = Individual()

        self.iterative_construct(self.genomeRoot, depth=depth-1, overall_depth=depth)

        return self

    def iterative_construct(self, node, depth, overall_depth):
        if depth <= 0:
            return

        for i in range(len(node.children)):
            if np.random.normal(CREATION_MU, CREATION_STD) < depth/overall_depth:
                node.children[i] = Node() #0R 1L 2F
                self.iterative_construct(node.children[i], depth-1, overall_depth)

    def get_nr_expressed_modules(self):
        if self._nr_expressed_modules == -1:
            self._nr_expressed_modules = self.recursive_counting(self.genomeRoot)
        return self._nr_expressed_modules

    def recursive_counting(self, node) -> int:
        count = 0
        for child in node.children:
            if child != None:
                count += self.recursive_counting(child)

        return 1 + count

    def genome_to_str(self):
        res = ""
        res += f"{self.genomeRoot.scale},{self.genomeRoot.controller.amp},{self.genomeRoot.controller.freq},{self.genomeRoot.controller.phase},{self.genomeRoot.controller.offset}"
        res += "|"

        child_strings = self.iterative_to_string(self.genomeRoot)
        child_strings = child_strings[:-2]
        return res + child_strings

    def iterative_to_string(self, node) -> str:
        res = ""
        num_children = len(node.occupied_spots_list())

        for _ in range(num_children-1):
            res += "[|"

        for i in node.occupied_spots_list():
            child = node.children[i]
            res += f"M{i},{child.angle},{child.scale},{child.controller.amp},{child.controller.freq},{child.controller.phase},{child.controller.offset}"
            res += "|" + self.iterative_to_string(child)

        if num_children == 0:
            res += "]|"

        return res

    def mutate(self, mutation_rate):
        # Mutation rate on each cell?
        # Larger creatures will mutate more. Volatile?
        # Mutation rate on creature
        # Larger creature will mutate less. Safer?

        self.needs_evaluation = False
        if np.random.rand() < mutation_rate:
            node_list = []

            intervals = {}
            intervals["control"]     = [0,                           0.2]
            intervals["angle"]       = [intervals["control"][1],     0.3]
            intervals["remove_node"] = [intervals["angle"][1],       0.5]
            intervals["add_node"]    = [intervals["remove_node"][1], 0.8]
            intervals["scale"]       = [intervals["add_node"][1],      1]

            is_in = lambda interval, x: interval[0] <= x <= interval[1]

            rand_num = np.random.rand()
            if is_in(intervals["control"], rand_num):
                self.traverse_get_list(self.genomeRoot, node_list)
                node_to_mutate = np.random.choice(node_list)
                if node_to_mutate.scale < 1: return
                node_to_mutate.controller.mutate()
            elif is_in(intervals["angle"], rand_num):
                self.traverse_get_list(self.genomeRoot, node_list)
                node_to_mutate = np.random.choice(node_list)
                node_to_mutate.angle += -90 if np.random.rand() <= 0.5 else 90
                if node_to_mutate.angle < 0:
                    node_to_mutate.angle = 270
                elif node_to_mutate.angle > 270:
                    node_to_mutate.angle = 0
            elif is_in(intervals["remove_node"], rand_num):
                self.get_almost_leaf_nodes(self.genomeRoot, node_list)
                if len(node_list) == 0: return
                node_to_mutate = np.random.choice(node_list)
                node_to_mutate.children[np.random.choice(node_to_mutate.occupied_spots_list())] = None
            elif is_in(intervals["add_node"], rand_num):
                self.get_not_filled_nodes(self.genomeRoot, node_list)
                node_to_mutate = np.random.choice(node_list)
                new_node = Node()
                node_to_mutate.children[np.random.choice(node_to_mutate.open_spots_list())] = new_node
                new_node.scale = 0.1
                new_node.controller.amp = 0.0
                new_node.controller.freq = 0.0
                new_node.controller.phase = 0.0
                new_node.controller.offset = 0.0
            elif is_in(intervals["scale"], rand_num):
                self.traverse_get_list(self.genomeRoot, node_list)
                node_to_mutate = np.random.choice(node_list)
                node_to_mutate.scale += (np.random.rand() - 0.5)*0.2
                node_to_mutate.scale = bounce_back(node_to_mutate.scale, (0.1, 3))

            self.needs_evaluation = True
            self._nr_expressed_modules = -1

    def traverse_get_list(self, node, node_list):
        node_list.append(node)

        for child in node.children:
            if child is not None:
                self.traverse_get_list(child, node_list)

    def get_not_filled_nodes(self, node, node_list):
        filled = True
        for child in node.children:
            if child is not None:
                self.get_not_filled_nodes(child, node_list)
            else:
                filled = False
        if not filled:
            node_list.append(node)

    def get_almost_leaf_nodes(self, node, node_list):
        almost_leaf = True
        for child in node.children:
            if child is not None and not child.is_leaf():
                almost_leaf = False
                self.get_almost_leaf_nodes(child, node_list)

        if len(node.occupied_spots_list()) != 0 and almost_leaf:
            node_list.append(node)
