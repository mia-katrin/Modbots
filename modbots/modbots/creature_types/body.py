import numpy as np
import pickle

from modbots.util import bool_from_distribution, add_on_result, traverse_get_list
from modbots.creature_types.node import Node

class Body:
    def __init__(self, variable_scale=False, gene=None):
        self.root = Node()
        self._nr_expressed_modules = -1
        if gene != None:
            self._interpret_string_gene(gene)

        self.mutation_history = []

    @staticmethod
    def random(config):
        self = Body(config.individual.variable_scale)
        self._recursive_construct(self.root, config, depth=config.individual.ind_depth-1)

        if config.individual.force_interesting:
            while self.get_nr_modules() < 3:
                self = Body(config.individual.variable_scale)
                self._recursive_construct(self.root, config, depth=config.individual.ind_depth-1)

        return self

    def _recursive_construct(self, node, config, depth):
        if depth <= 0:
            return

        for i in range(len(node.children)):
            if bool_from_distribution("gaussian", c_mu=config.individual.creation_mu, c_std=config.individual.creation_std, depth=depth, o_depth=config.individual.ind_depth):
                node.children[i] = Node() #0F 1R 2L
                self._recursive_construct(node.children[i], config, depth-1)

    def _recursive_counting(self, node) -> int:
        count = 0
        for child in node.children:
            if child != None:
                count += self._recursive_counting(child)

        return 1 + count

    def _recursive_to_string(self, node) -> str:
        res = ""
        num_children = len(node.occupied_spots_list())

        for _ in range(num_children-1):
            res += "[|"

        for i in node.occupied_spots_list():
            child = node.children[i]
            res += f"M{i},{child.angle},{child.scale}"
            res += "|" + self._recursive_to_string(child)

        if num_children == 0:
            res += "]|"

        return res

    def _interpret_string_gene(self, gene):
        gene = np.array(gene.split("|"))
        root_info = np.array(gene[0].split(",")).astype(float)
        self.root.scale = root_info[0]

        pretend_stack = []
        node = self.root

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

                node = child

            elif info[0] == "[":
                # node on stack
                pretend_stack.append(node)
            elif info[0] == "]":
                # Node off stack
                node = pretend_stack.pop()

    def get_nr_modules(self):
        if self._nr_expressed_modules == -1:
            self._nr_expressed_modules = self._recursive_counting(self.root)
        return self._nr_expressed_modules

    def to_str(self):
        res = ""
        res += f"{self.root.scale}"
        res += "|"

        child_strings = self._recursive_to_string(self.root)
        child_strings = child_strings[:-2]
        return res + child_strings

    def mutate_maybe(self, config):
        individual_likelihood = config.mutation.body/self.get_nr_modules()

        current_nodes = [self.root]

        result = ""

        while len(current_nodes) > 0:
            node = current_nodes.pop(0)

            node_mutation = node.mutate_maybe(config, individual_likelihood)
            result = add_on_result(
                node_mutation,
                result
            )

            for child in node.children:
                if child != None:
                    current_nodes.append(child)

        if result != "":
            self._nr_expressed_modules = -1
            return result

        return None

    def mutate(self, config):
        mutated = False

        node_chance = 1/self.get_nr_modules()

        current_nodes = [self.root]

        while len(current_nodes) > 0:
            node = current_nodes.pop(0)

            if np.random.rand() <= node_chance:
                mut_type = node.mutate(config)
                if mut_type != "None":
                    if mutated:
                        self.mutation_history[-1] += ", " + mut_type
                    else:
                        self.mutation_history.append(mut_type)
                    mutated = True

            for child in node.children:
                if child != None:
                    current_nodes.append(child)

        if not mutated: # Force body mutate
            return self.mutate(config)

        self._nr_expressed_modules = -1
        return mutated
