import copy
import numpy as np

from modbots.creature_types.node import Node
from modbots.util import bool_from_distribution

from modbots.creature_types.abstract_individual import AbstractIndividual

CREATION_MU = 0.75 # Higher means fewer average modules
CREATION_STD = 0.35 # Higher means more variance in number of modules

class Individual(AbstractIndividual):
    def __init__(self, gene=None):
        self.bodyRoot = Node()
        self.bodyRoot.angle = 0
        self.fitness = -1
        self.needs_evaluation = True
        self._nr_expressed_modules = -1
        if gene is not None:
            self.interpret_string_gene(gene)

    def interpret_string_gene(self, gene):
        gene = np.array(gene.split("|"))
        root_info = np.array(gene[0].split(",")).astype(float)
        self.bodyRoot.scale = root_info[0]
        self.bodyRoot.controller.amp = root_info[1]
        self.bodyRoot.controller.freq = root_info[2]
        self.bodyRoot.controller.phase = root_info[3]
        self.bodyRoot.controller.offset = root_info[4]

        pretend_stack = []
        node = self.bodyRoot

        for info in gene:
            if info == "":
                pass
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

    def prepare_for_evaluation(self):
        allNodes = []
        self.traverse_get_list(self.bodyRoot, allNodes)

        # Ensure all controllers are reset
        for node in allNodes:  # All controllers
            node.controller.reset()

    def get_actions(self, observation):
        actions = np.zeros(shape=(1,50),dtype=np.float32)

        allNodes = []
        self.traverse_get_list(self.bodyRoot, allNodes)

        for j, node in enumerate(allNodes):  # All controllers
            action = node.controller.update(0.05)
            actions[0,j] = action

        return actions

    @staticmethod
    def random(depth):
        self = Individual()

        self.iterative_construct(self.bodyRoot, depth=depth-1, overall_depth=depth)

        while self.get_nr_modules() <= 2 or \
              (self.bodyRoot.scale < 1 and self.bodyRoot.children[0] == None) or \
              (self.bodyRoot.scale < 1 and self.bodyRoot.children[0].scale < 1):
            self = Individual()
            self.iterative_construct(self.bodyRoot, depth=depth-1, overall_depth=depth)

        return self

    def iterative_construct(self, node, depth, overall_depth):
        if depth <= 0:
            return

        for i in range(len(node.children)):
            if bool_from_distribution("gaussian", c_mu=CREATION_MU, c_std=CREATION_STD, depth=depth, o_depth=overall_depth):
                node.children[i] = Node() #0F 1R 2L
                self.iterative_construct(node.children[i], depth-1, overall_depth)

    def get_nr_modules(self):
        if self._nr_expressed_modules == -1:
            self._nr_expressed_modules = self.recursive_counting(self.bodyRoot)
        return self._nr_expressed_modules

    def recursive_counting(self, node) -> int:
        count = 0
        for child in node.children:
            if child != None:
                count += self.recursive_counting(child)

        return 1 + count

    def body_to_str(self):
        res = ""
        res += f"{self.bodyRoot.scale},{self.bodyRoot.controller.amp},{self.bodyRoot.controller.freq},{self.bodyRoot.controller.phase},{self.bodyRoot.controller.offset}"
        res += "|"

        child_strings = self.iterative_to_string(self.bodyRoot)
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

    def crossover(self, other) -> tuple:
        child1 = Individual()
        child2 = Individual()
        child1.bodyRoot = copy.deepcopy(self.bodyRoot)
        child2.bodyRoot = copy.deepcopy(other.bodyRoot)

        self_branch = np.random.choice([0,1,2])
        other_branch = np.random.choice([0,1,2])

        child1.bodyRoot.children[self_branch] = other.bodyRoot.children[other_branch]
        child2.bodyRoot.children[other_branch] = self.bodyRoot.children[self_branch]

        return child1, child2

    def mutate(self, mutation_rate):
        if self.fitness >= 0:
            self.needs_evaluation = False
        size = self.get_nr_modules()
        mutated = self.bodyRoot.mutate_breadth(mutation_rate/size)
        if mutated:
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
