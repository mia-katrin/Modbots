from individual import Individual, Node
import unittest

class TestIndNNode(unittest.TestCase):
    def test_init_Node(self):
        node = Node()
        assert node.angle % 90 == 0
        assert len(node.children) == 3
        assert node.children[0] == node.children[1] == node.children[2] == None

    def test_spots_list_Node(self):
        node = Node()
        child = Node()
        node.children[0] = child
        assert node.children == [child, None, None]
        assert node.open_spots_list() == [1,2]
        assert node.occupied_spots_list() == [0]

    def test_is_leaf_Node(self):
        node = Node()
        child = Node()
        node.children[0] = child

        assert node.is_leaf() == False # Testing partial leaf
        assert child.is_leaf() == True # Testing solid leaf

        node.children[1] = Node()
        node.children[2] = Node()

        assert node.is_leaf() == False # Testing non-leaf

    def test_init_str_Individual(self):
        # Init that's never really used
        ind = Individual()

        assert ind.fitness == 0
        # At this time I don't require anything out of this version of init

        # Init with string input
        # scale, controlvalues | M child_index, angle, scale, controlvalues
        gene = "1.0,9.0,8.0,7.0,6.0|[|M0,90,1.0,0.0,0.0,0.0,0.0|]|M1,0,1.0,1.0,2.0,3.0,4.0|M2,0,1.0,1.0,2.0,3.0,4.0|"
        ind = Individual(gene)

        ind.genomeRoot.scale == 1.0
        ind.genomeRoot.controller.phase == 7.0
        ind.genomeRoot.children[0].angle == 90
        ind.genomeRoot.children[1].angle == 0
        ind.genomeRoot.children[1].controller.freq == 2.0

        assert ind.genome_to_str() == gene

    def test_get_nr_expressed_modules(self):
        ind = Individual()
        ind.genomeRoot.children = [None, Node(), Node()]
        ind.genomeRoot.children[1].children = [Node(), None, Node()]
        ind.genomeRoot.children[2].children = [None, None, Node()]
        ind.genomeRoot.children[2].children[2].children = [None, None, Node()]

        assert ind.get_nr_expressed_modules() == 7

        gene = "1.0,9.0,8.0,7.0,6.0|[|M0,90,1.0,0.0,0.0,0.0,0.0|]|M1,0,1.0,1.0,2.0,3.0,4.0|M2,0,1.0,1.0,2.0,3.0,4.0|"
        ind = Individual(gene)
        assert ind.get_nr_expressed_modules() == 4

    def test_mutation(self):
        ind = Individual()
        ind.genomeRoot.children = [None, Node(), Node()]
        ind.genomeRoot.children[1].children = [Node(), None, Node()]
        ind.genomeRoot.children[2].children = [None, None, Node()]
        ind.genomeRoot.children[2].children[2].children = [None, None, Node()]

        ind.mutate(mutation_rate=0)
        assert ind.needs_evaluation == False
        ind.mutate(mutation_rate=1)
        assert ind.needs_evaluation == True

    def traverse_get_list(self):
        ind = Individual()
        ind.genomeRoot.children = [None, Node(), Node()]
        ind.genomeRoot.children[1].children = [Node(), None, Node()]
        ind.genomeRoot.children[2].children = [None, None, Node()]
        ind.genomeRoot.children[2].children[2].children = [None, None, Node()]

        node_list = []
        ind.traverse_get_list(ind.genomeRoot)


if __name__ == '__main__':
    unittest.main()
