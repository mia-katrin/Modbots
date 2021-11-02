from individual import Individual, Node
import unittest
import copy

class TestIndNNode(unittest.TestCase):
    def test_init_Node(self):
        node = Node()
        assert node.angle % 90 == 0
        assert len(node.children) == 3
        assert node.children[0] == node.children[1] == node.children[2] == None

    def test_node_mutate(self):
        node = Node("random")
        node.children = [Node("random"), Node("random"), None]
        node.children[0].children = [Node("random"), None, Node("random")]
        node.children[1].children = [Node("random"), None, Node("random")]

        #   o
        #   |\
        #   o o
        #  /\ /\
        # o o o o

        def is_all_equal(node1, node2):
            fasit = [node1]
            to_check = [node2]

            while len(fasit) > 0 and len(to_check) > 0:
                elem1 = fasit.pop(0)
                elem2 = to_check.pop(0)

                if elem1 == None and elem2 == None:
                    continue

                if (elem1 == None and elem2 != None) or \
                    (elem2 == None and elem1 != None) or \
                    (elem1.scale != elem2.scale) or \
                    (elem1.angle != elem2.angle) or \
                    (elem1.controller.amp != elem2.controller.amp) or \
                    (elem1.controller.freq != elem2.controller.freq) or \
                    (elem1.controller.phase != elem2.controller.phase) or \
                    (elem1.controller.offset != elem2.controller.offset):
                    """if elem1 == None and elem2 != None:
                            print("Elem1 is None, elem2 is Ind")
                        if elem2 == None and elem1 != None:
                            print("Elem2 is None, elem1 is Ind")
                        if elem1.scale != elem2.scale:
                            print(f"Scale: {elem1.scale}, {elem2.scale}")
                        if elem1.controller.amp != elem2.controller.amp:
                            print(f"Amp: {elem1.controller.amp}, {elem2.controller.amp}")
                        if elem1.controller.freq != elem2.controller.freq:
                            print(f"Freq: {elem1.controller.freq}, {elem2.controller.freq}")
                        if elem1.controller.phase != elem2.controller.phase:
                            print(f"Phase: {elem1.controller.phase}, {elem2.controller.phase}")
                        if elem1.controller.offset != elem2.controller.offset:
                            print(f"Offset: {elem1.controller.offset}, {elem2.controller.offset}")"""
                    return False

                if elem1 != None:
                    for child in elem1.children:
                        fasit.append(child)

                if elem2 != None:
                    for child in elem2.children:
                        to_check.append(child)

            if len(fasit) != len(to_check):
                return False
            return True

        for _ in range(100):
            node = Node("random")
            deepcopy_node = copy.deepcopy(node)
            node.mutate()
            assert is_all_equal(deepcopy_node, node) == False

        matrix = [[0,0],[0,0]]
        for i in range(100):
            deepcopy_node = copy.deepcopy(node)
            needs_muation = node.mutate_breadth(0.1/7)
            matrix[needs_muation][is_all_equal(deepcopy_node, node)] += 1

            if needs_muation and is_all_equal(node, deepcopy_node):
                print(node.__dict__)
                print(node.__dict__["controller"].__dict__)
                print(deepcopy_node.__dict__)
                print(deepcopy_node.__dict__["controller"].__dict__)
        print(matrix)
        assert matrix[0][0] == 0 and matrix[1][1] == 0, matrix

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

        assert ind.fitness == -1
        # At this time I don't require anything out of this version of init

        # Init with string input
        # scale, controlvalues | M child_index, angle, scale, controlvalues
        gene = "1.0,9.0,8.0,7.0,6.0|[|M0,90,1.0,0.0,0.0,0.0,0.0|]|M1,0,1.0,1.0,2.0,3.0,4.0|M2,0,1.0,1.0,2.0,3.0,4.0|"
        ind = Individual(gene)

        ind.bodyRoot.scale == 1.0
        ind.bodyRoot.controller.phase == 7.0
        ind.bodyRoot.children[0].angle == 90
        ind.bodyRoot.children[1].angle == 0
        ind.bodyRoot.children[1].controller.freq == 2.0

        assert ind.body_to_str() == gene

    def test_get_nr_expressed_modules(self):
        ind = Individual()
        ind.bodyRoot.children = [None, Node(), Node()]
        ind.bodyRoot.children[1].children = [Node(), None, Node()]
        ind.bodyRoot.children[2].children = [None, None, Node()]
        ind.bodyRoot.children[2].children[2].children = [None, None, Node()]

        assert ind.get_nr_expressed_modules() == 7

        gene = "1.0,9.0,8.0,7.0,6.0|[|M0,90,1.0,0.0,0.0,0.0,0.0|]|M1,0,1.0,1.0,2.0,3.0,4.0|M2,0,1.0,1.0,2.0,3.0,4.0|"
        ind = Individual(gene)
        assert ind.get_nr_expressed_modules() == 4

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
