from modbots.creature_types.body import Body
import unittest
import copy

class TestBody(unittest.TestCase):
    def get_config(self):
        # A fake config to help me test
        class IndividualConf:
            def __init__(self):
                self.growing = True
                self.variable_scale = False
                self.force_interesting = True
                self.ind_depth = 5
                self.creation_mu = 0.75
                self.creation_std = 0.35
        class MutationConf:
            def __init__(self):
                self.angle = 0.1
                self.remove_node = 0.3
                self.add_node = 0.4
                self.scale = 0.2
                self.copy_branch = 0.2
        class Config:
            def __init__(self):
                self.individual = IndividualConf()
                self.mutation = MutationConf()

        return Config()

    def get_nodes_list(self, body):
        """ Own function to get all body's nodes
        """
        nodes = [body.root]
        index = 0
        while index < len(nodes):
            node = nodes[index]
            index += 1

            for child in node.children:
                if child != None:
                    nodes.append(child)

        return nodes

    def test_init(self):
        # Empty init
        body = Body()
        assert len(body.root.open_spots_list()) == 3

        # Bodies should be created equal no matter the encoding
        body = Body(variable_scale=True)
        assert body.root.scale == 1.0

        # Init with string input
        # scale, controlvalues | M child_index, angle, scale, controlvalues
        gene = "1.0|[|M0,90,1.0|]|M1,0,1.0|M2,0,1.0|"
        body = Body(gene=gene)

        body.root.scale == 1.0
        body.root.children[0].angle == 90
        body.root.children[1].angle == 0

        # The to_str function should return the Unity readable version of body
        # It should correspond to the string version above
        assert body.to_str() == gene

        # variabe scale sould not effect the reading of a gene
        body = Body(variable_scale=True, gene=gene)
        assert body.to_str() == gene

    def test_random(self):
        """ Random is a static function to initiate a random body
        """
        config = self.get_config()
        config.individual.force_interesting = True

        config.individual.variable_scale = False
        body = Body.random(config)
        nodes = self.get_nodes_list(body)
        assert len(nodes) >= 3, "Force interesting doesn't work"

        # All bodies should be initiated with 1.0 in module length
        assert list(map(lambda x: x.scale == 1., nodes)) == [True for _ in range(len(nodes))]

        # Even with variable scale
        config.individual.variable_scale = True
        body = Body.random(config)
        nodes = self.get_nodes_list(body)
        assert list(map(lambda x: x.scale == 1., nodes)) == [True for _ in range(len(nodes))]

    def test_get_nr_modules(self):
        body = Body()
        assert body.get_nr_modules() == 1

        body.root.children[0] = type(body.root)()
        body.root.children[1] = type(body.root)()
        body.root.children[2] = type(body.root)()
        body.root.children[2].children[0] = type(body.root)()
        body.root.children[2].children[1] = type(body.root)()
        body.root.children[2].children[2] = type(body.root)()
        body._nr_expressed_modules = -1
        assert body.get_nr_modules() == 7

    def test_to_str(self):
        """ The to_str function is very important because it's how Unity reads
        a body and constructs it
        """
        gene = "1.0|[|M0,90,1.0|]|M1,0,1.0|M2,0,1.0|"
        body = Body(gene=gene)
        assert body.to_str() == gene

        body = Body()
        body.root.children[0] = type(body.root)()
        body.root.children[0].angle = 0
        body.root.children[1] = type(body.root)()
        body.root.children[1].angle = 90
        body.root.children[2] = type(body.root)()
        body.root.children[2].angle = 0
        body.root.children[2].scale = 2.2
        body.root.children[2].children[0] = type(body.root)()
        body.root.children[2].children[0].angle = 0

        gene = "1.0|[|[|M0,0,1.0|]|M1,90,1.0|]|M2,0,2.2|M0,0,1.0|"
        assert body.to_str() == gene

    def test_mutate(self):
        config = self.get_config()
        config.mutation.angle = 0.2
        config.mutation.remove_node = 0.2
        config.mutation.add_node = 0.2
        config.mutation.scale = 0.2
        config.mutation.copy_branch = 0.2

        config.individual.variable_scale = True
        config.individual.growing = False

        # Testing that mutate really forces a mutation (a difference)
        for _ in range(100):
            body = Body.random(config)
            nodes = self.get_nodes_list(body)

            body2 = copy.deepcopy(body)
            body2.mutate(config)
            nodes_mut = self.get_nodes_list(body2)

            # If they're not equal in length, an addition or removal has happened
            # Otherwise we must check that the nodes are changed
            if len(nodes) == len(nodes_mut):
                mutated = False
                for node1, node2 in zip(nodes, nodes_mut):
                    if node1.scale != node2.scale or node1.angle != node2.angle or node1.open_spots_list() != node2.open_spots_list():
                        print(node1.__dict__, node2.__dict__)
                        mutated = True
                assert mutated
