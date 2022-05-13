from modbots.creature_types.configurable_individual import Individual
from modbots.creature_types.configurable_individual import Individual
import unittest
import copy

class TestIndNNode(unittest.TestCase):

    def test_order_mut_cross(self):
        ind = Individual.random(5)
        assert ind.needs_evaluation
        assert ind.fitness == -1

        ind.mutate(1)
        assert ind.needs_evaluation
        ind.needs_evaluation = False
        ind.fitness = 10
        child1, child2 = ind.crossover(Individual.random(5))

        assert not ind.needs_evaluation
        assert child1.needs_evaluation
        assert child1.fitness == -1

    def test_mutation(self):
        ind = Individual()
        ind.bodyRoot.children = [None, Node("random"), Node("random")]
        ind.bodyRoot.children[1].children = [Node("random"), None, Node("random")]
        ind.bodyRoot.children[2].children = [None, None, Node("random")]
        ind.bodyRoot.children[2].children[2].children = [None, None, Node("random")]

        ind.needs_evaluation = False
        ind.fitness = 10
        ind.mutate(mutation_rate=0)
        assert ind.needs_evaluation == False
        ind.mutate(mutation_rate=100)
        assert ind.needs_evaluation == True

    def traverse_get_list(self):
        ind = Individual()
        ind.bodyRoot.children = [None, Node(), Node()]
        ind.bodyRoot.children[1].children = [Node(), None, Node()]
        ind.bodyRoot.children[2].children = [None, None, Node()]
        ind.bodyRoot.children[2].children[2].children = [None, None, Node()]

        node_list = []
        ind.traverse_get_list(ind.bodyRoot)


if __name__ == '__main__':
    unittest.main()
