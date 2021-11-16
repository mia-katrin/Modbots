"""Abstract methods that are rquired by evaluate and evolve"""

from abc import ABC, abstractmethod
from modbots.creature_types.node import Node

from modbots.util import bool_from_distribution

CREATION_MU = 0.75 # Higher means fewer average modules
CREATION_STD = 0.35 # Higher means more variance in number of modules

class AbstractIndividual:
    def __init__(self, gene=None, controller_class=None):
        self.bodyRoot = Node(controller = controller_class() if controller_class != None else None)
        self.fitness = -1
        self.needs_evaluation = True
        self._nr_expressed_modules = -1
        if gene is not None:
            self.interpret_string_gene(gene)

    def random_ind(self, depth, controller_class=None):
        self._iterative_construct(self.bodyRoot, depth=depth-1, overall_depth=depth, controller_class=controller_class)

        while self.get_nr_modules() <= 2 or \
            (self.bodyRoot.scale < 1 and self.bodyRoot.children[0] == None) or \
            (self.bodyRoot.scale < 1 and self.bodyRoot.children[0].scale < 1):
            print(self.get_nr_modules())
            self = type(self)()
            self._iterative_construct(self.bodyRoot, depth=depth-1, overall_depth=depth, controller_class=controller_class)

        return self

    def _iterative_construct(self, node, depth, overall_depth, controller_class=None):
        if depth <= 0:
            return

        for i in range(len(node.children)):
            if bool_from_distribution("gaussian", c_mu=CREATION_MU, c_std=CREATION_STD, depth=depth, o_depth=overall_depth):
                node.children[i] = Node(controller = controller_class() if controller_class != None else None) #0F 1R 2L
                self._iterative_construct(node.children[i], depth-1, overall_depth, controller_class)

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

    @abstractmethod
    def interpret_string_gene(self, gene):
        pass

    @abstractmethod
    def get_actions(self, observation):
        pass

    @abstractmethod
    def prepare_for_evaluation(self):
        pass

    @abstractmethod
    def ind_to_str(self):
        pass

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

    def mutate(self, config):
        if self.fitness >= 0:
            self.needs_evaluation = False
        size = self.get_nr_modules()
        mutated = self.bodyRoot.mutate_breadth(config.ea.mut_rate/size)
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

    def body_to_str(self):
        return self.to_str(with_control=False)

    def to_str(self, with_control=True):
        res = ""
        res += f"{self.bodyRoot.scale}"
        if with_control:
            res += f",{self.bodyRoot.controller.amp},{self.bodyRoot.controller.freq},{self.bodyRoot.controller.phase},{self.bodyRoot.controller.offset}"
        res += "|"

        child_strings = self.iterative_to_string(self.bodyRoot, with_control)
        child_strings = child_strings[:-2]
        return res + child_strings

    def iterative_to_string(self, node, with_control=True) -> str:
        res = ""
        num_children = len(node.occupied_spots_list())

        for _ in range(num_children-1):
            res += "[|"

        for i in node.occupied_spots_list():
            child = node.children[i]
            res += f"M{i},{child.angle},{child.scale}"
            if with_control:
                res += f",{child.controller.amp},{child.controller.freq},{child.controller.phase},{child.controller.offset}"
            res += "|" + self.iterative_to_string(child, with_control)

        if num_children == 0:
            res += "]|"

        return res
