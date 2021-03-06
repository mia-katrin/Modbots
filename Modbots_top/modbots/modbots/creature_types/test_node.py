from modbots.creature_types.node import Node
import unittest
import copy

class TestNode(unittest.TestCase):
    def get_config(self):
        # A fake config to help me test
        class IndividualConf:
            def __init__(self):
                self.growing = True
                self.variable_scale = False
                self.gradual = False
        class MutationConf:
            def __init__(self):
                self.angle = 0.1
                self.remove_node = 0.3
                self.add_node = 0.4
                self.scale = 0.2
                self.copy_branch = 0.2

                self.body = 0.5
        class EAConf:
            def __init__(self):
                self.body_sigma = 0.1
        class Config:
            def __init__(self):
                self.individual = IndividualConf()
                self.mutation = MutationConf()
                self.ea = EAConf()

        return Config()

    def test_init(self):
        node = Node(variable_scale=False, growing=False)
        assert node.angle % 90 == 0
        assert len(node.children) == 3
        assert node.children[0] == node.children[1] == node.children[2] == None
        assert node.scale == 1.0

        # Variable scale should init with a different scale
        node = Node(variable_scale=True, growing=False)
        assert node.scale != 1.0, "Sometimes this does happen tho. Run again."

        # Growing should init as a small module
        node = Node(variable_scale=False, growing=True)
        assert node.scale == 0.05

        # Growing takes presedence to variable scale
        node = Node(variable_scale=True, growing=True)
        assert node.scale == 0.05

    def test_spots_list(self):
        """ Node has three functions to test children spots for factors, such as
        open, occupied, and custom. I use the custom to check for leaves, so that
        is tested for accuracy.
        """
        node = Node()
        child = Node()
        node.children[0] = child
        assert node.children == [child, None, None]
        assert node.open_spots_list() == [1,2]
        assert node.occupied_spots_list() == [0]
        assert node.get_indexes_of(lambda x: x is not None and x.is_leaf()) == [0]

        # Make child now a non-leaf
        child.children = [Node(), None, None]
        assert node.get_indexes_of(lambda x: x is not None and x.is_leaf()) == []

    def test_is_leaf(self):
        node = Node()
        child = Node()
        node.children[0] = child

        assert node.is_leaf() == False # Testing partial leaf
        assert child.is_leaf() == True # Testing solid leaf

        node.children[1] = Node()
        node.children[2] = Node()

        assert node.is_leaf() == False # Testing non-leaf

    def test_mutate_angle(self):
        """ This function should always mutate angle
        """
        config = self.get_config()

        node = Node()

        times = {"0":0, "90":0, "180":0, "270":0}

        config.individual.growing = False
        for _ in range(10000):
            old_angle = node.angle
            node.mutate_angle(config)
            assert old_angle != node.angle
            times[str(node.angle)] += 1

        config.individual.growing = True
        for _ in range(10000):
            old_angle = node.angle
            node.mutate_angle(config)
            assert old_angle != node.angle
            times[str(node.angle)] += 1

        print(times)
        for key in times:
            assert times[key] > 10000/4

    def test_mutate_remove_leaf(self):
        # Removing from a leaf node always yields None
        config = self.get_config()
        node = Node()

        for grad_bool in [True, False]:
            for grow_bool in [True, False]:
                for vars_bool in [True, False]:
                    config.individual.gradual = grad_bool
                    config.individual.growing = grow_bool
                    config.individual.variable_scale = vars_bool
                    assert node.mutate_remove(config) == None

    def test_mutate_remove_normal(self):
        config = self.get_config()
        config.individual.growing = False
        config.individual.gradual = False

        for vars_bool in [True, False]:
            config.individual.variable_scale = vars_bool
            node = Node()
            node.children[0] = Node()

            assert node.mutate_remove(config) == "Remove full"
            assert node.mutate_remove(config) == None

    def test_mutate_remove_dwarf(self):
        config = self.get_config()
        config.individual.growing = True
        config.individual.gradual = False
        node = Node()
        node.children[0] = Node()
        node.children[0].scale = 1

        result = node.mutate_remove(config)
        assert result.startswith("Remove")
        try:
            float(result.split(" ")[1])
        except:
            assert False, "Last part is not float"
        assert node.mutate_remove(config) == None

        config.individual.growing = True
        config.individual.gradual = True
        node = Node()
        node.children[0] = Node()
        node.children[0].scale = 0.2

        result = node.mutate_remove(config)
        assert result.startswith("Remove")
        try:
            float(result.split(" ")[1])
        except:
            assert False, "Last part is not float"
        assert node.mutate_remove(config) == None

        config.individual.growing = True
        config.individual.gradual = True
        node = Node()
        node.children[0] = Node()
        node.children[0].scale = 1

        assert node.mutate_remove(config) == "Remove shrink"
        assert node.mutate_remove(config) != None

    def test_mutate_remove_shrink(self):
        config = self.get_config()
        config.individual.growing = True
        config.individual.gradual = True
        node = Node()
        node.children[0] = Node()

        while node.children[0].scale > 0.25:
            assert node.mutate_remove(config) == "Remove shrink"
        result = node.mutate_remove(config)
        assert result.startswith("Remove")
        try:
            float(result.split(" ")[1])
        except:
            assert False, "Last part is not float"
        assert node.mutate_remove(config) == None

    def test_mutate_add_node(self):
        config = self.get_config()
        config.individual.growing = False
        config.individual.gradual = False
        node = Node()

        assert node.mutate_add_node(config) == "Add on normal"
        assert node.mutate_add_node(config) == "Add on normal"
        assert node.mutate_add_node(config) == "Add on normal"
        assert node.mutate_add_node(config) == None

        config.individual.growing = True
        config.individual.gradual = True
        node = Node()
        node.scale = 0.05

        while node.scale < 1.0:
            assert node.mutate_add_node(config) == "Add on grow"
        result = node.mutate_add_node(config)
        assert result.startswith("Add on") and result != "Add on grow"

        config.individual.growing = True
        config.individual.gradual = False
        node = Node()
        node.scale = 0.05
        result = node.mutate_add_node(config)
        assert result.startswith("Add on") and result != "Add on grow"

    def test_mutate_scale(self):
        config = self.get_config()
        config.individual.growing = False
        config.individual.variable_scale = False
        node = Node()

        assert node.mutate_scale(config) == None

        config.individual.growing = True
        assert node.mutate_scale(config) == None

        node.scale = 0.05
        while node.scale < 1.0:
            old_val = node.scale
            node.mutate_scale(config)
            assert node.scale > old_val
        assert node.scale == 1.

        config.individual.variable_scale = True
        pos, neg = False, False
        for _ in range(1000):
            old_val = node.scale
            node.mutate_scale(config)
            if node.scale - old_val > 0:
                pos = True
            elif old_val - node.scale > 0:
                neg = True
        assert pos and neg

    def test_mutate_copy_branch(self):
        config = self.get_config()
        node = Node()

        assert node.mutate_copy_branch(config) == None

        node.children[0] = Node()
        assert node.mutate_copy_branch(config) == "Copy"
        assert node.children[1] != None or node.children[2] != None

        assert node.mutate_copy_branch(config) == "Copy"
        assert node.children[1] != None and node.children[2] != None

        assert node.mutate_copy_branch(config) == None

    def test_interval_func(self):
        node = Node()
        func, so_far = node._interval_func(0, 0.1)

        assert so_far == 0.1
        assert func(0) == True
        assert func(0.1) == False

        func, so_far = node._interval_func(0.4, 0.3)

        assert so_far == 0.7
        assert func(0) == False
        assert func(0.4) == True
        assert func(0.7) == False
        assert func(0.8) == False

    def test_mutate(self):
        config = self.get_config()
        config.mutation.angle = 0.2
        config.mutation.remove_node = 0.2
        config.mutation.add_node = 0.2
        config.mutation.scale = 0.2
        config.mutation.copy_branch = 0.2

        config.individual.variable_scale = True
        config.individual.growing = False

        times = {"Angle":0, "Remove":0, "Add":0, "Scale":0, "Copy":0}
        for _ in range(1000):
            node = Node()
            node.children[0] = Node()
            mutation = node.mutate(config)
            assert mutation != "None"

            if mutation.startswith("Angle"):
                times["Angle"] += 1
            elif mutation.startswith("Remove"):
                times["Remove"] += 1
            elif mutation.startswith("Add"):
                times["Add"] += 1
            elif mutation.startswith("Scale"):
                times["Scale"] += 1
            elif mutation.startswith("Copy"):
                times["Copy"] += 1

        print(times)
        for key in times:
            assert times[key] > 100

        config.individual.growing = True

        times = {"Angle":0, "Remove":0, "Add":0, "Scale":0, "Copy":0}
        for _ in range(1000):
            node = Node()
            node.children[0] = Node()
            mutation = node.mutate(config)
            assert mutation != "None"

            if mutation.startswith("Angle"):
                times["Angle"] += 1
            elif mutation.startswith("Remove"):
                times["Remove"] += 1
            elif mutation.startswith("Add"):
                times["Add"] += 1
            elif mutation.startswith("Scale"):
                times["Scale"] += 1
            elif mutation.startswith("Copy"):
                times["Copy"] += 1

        print(times)
        for key in times:
            assert times[key] > 100

    def test_mutate_maybe(self):
        config = self.get_config()
        config.mutation.angle = 0.2
        config.mutation.remove_node = 0.2
        config.mutation.add_node = 0.2
        config.mutation.scale = 0.2
        config.mutation.copy_branch = 0.2

        config.individual.variable_scale = True
        config.individual.growing = False

        times = {"Angle":0, "Remove":0, "Add":0, "Scale":0, "Copy":0, "None":0}
        for _ in range(10000):
            node = Node()
            node.children[0] = Node()
            mutation = node.mutate_maybe(config,0.1)

            if mutation != None:
                mutations = mutation[1:-1].split(", ")
            else:
                mutations = [None]

            for mut in mutations:
                if mut == None:
                    times["None"] += 1
                elif mut.startswith("Angle"):
                    times["Angle"] += 1
                elif mut.startswith("Remove"):
                    times["Remove"] += 1
                elif mut.startswith("Add"):
                    times["Add"] += 1
                elif mut.startswith("Scale"):
                    times["Scale"] += 1
                elif mut.startswith("Copy"):
                    times["Copy"] += 1

        for key in times:
            if key == "None":
                assert 8000 < times[key] < 9500
            else:
                assert 100 < times[key] < 300, key

if __name__ == '__main__':
    unittest.main()
