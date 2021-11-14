import numpy as np
import neat
import os
import copy

from modbots.creature_types.abstract_individual import AbstractIndividual
from modbots.creature_types.node import Node

class Individual(AbstractIndividual):
    static_genome_key = 1

    def __init__(self, gene=None):
        super(Individual, self).__init__(controller_class=None, gene=gene)

    @staticmethod
    def random(depth):
        self = Individual()

        self = self.random_ind(depth, controller_class=None)

        # Make config
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-ctrnn-3to1')
        self.config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path)

        self.controllerGenome = neat.genome.DefaultGenome(Individual.static_genome_key)
        Individual.static_genome_key += 1
        self.controllerGenome.configure_new(self.config.genome_config)
        self.controller = neat.ctrnn.CTRNN.create(self.controllerGenome, self.config, 0.02)

        return self

    def interpret_string_gene(self, gene):
        pass

    def interpret_body_string(self, gene):
        gene = np.array(gene.split("|"))
        root_info = np.array(gene[0].split(",")).astype(float)
        self.bodyRoot.scale = root_info[0]

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

                node = child

            elif info[0] == "[":
                # node on stack
                pretend_stack.append(node)
            elif info[0] == "]":
                # Node off stack
                node = pretend_stack.pop()

    def get_actions(self, observation):
        actions = []

        i = 0
        for cont in self.controller_list:
            action = cont.advance(observation[i:i+3], advance_time=0.02, time_step=0.02)
            actions.append(action[0])
            i += 3

        to_ret = np.pad(
            np.array([actions]),
            ((0, 0), (0, 50 - len(self.controller_list))),
            'constant',
            constant_values=0
        )
        return to_ret

    def prepare_for_evaluation(self):
        self.controller.reset()

        allNodes = []
        self.traverse_get_list(self.bodyRoot, allNodes)

        self.controller_list = [
            copy.deepcopy(self.controller) for _ in range(len(allNodes))
        ]

    def ind_to_str(self):
        ind = self.body_to_str()

        # Do something abt controller

        return ind

    def mutate(self, mutation_rate):
        if self.fitness >= 0:
            self.needs_evaluation = False
        if np.random.rand() < mutation_rate*2/10:
            self.needs_evaluation = True
            self._nr_expressed_modules = -1
            self.controllerGenome.mutate(self.config.genome_config)
            print("Control mutate!")
        size = self.get_nr_modules()
        mutated = self.bodyRoot.mutate_breadth((mutation_rate*8/10)/size)
        if mutated:
            self.needs_evaluation = True
            self._nr_expressed_modules = -1
