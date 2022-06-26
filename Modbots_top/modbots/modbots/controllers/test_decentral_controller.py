from modbots.controllers.decentral_controller import DecentralController
from modbots.controllers.sine_controller import SineController
from modbots.creature_types.body import Body
from modbots.util import traverse_get_list
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
                self.ind_depth = 5
                self.creation_mu = 0.73
                self.creation_std = 0.35
                self.force_interesting = True
        class MutationConf:
            def __init__(self):
                self.angle = 0.1
                self.remove_node = 0.3
                self.add_node = 0.4
                self.scale = 0.2
                self.copy_branch = 0.2

                self.body = 0.5
                self.control = 0.5
        class EAConf:
            def __init__(self):
                self.body_sigma = 0.5
                self.control_sigma = 0.5
        class Config:
            def __init__(self):
                self.individual = IndividualConf()
                self.mutation = MutationConf()
                self.ea = EAConf()

        return Config()

    def test_mutate_maybe(self):
        def true_on_x_func(x, i):
            return i == x

        mutated = False
        for i in range(5):
            res = true_on_x_func(3, i)
            print(res)
            mutated = mutated or res

        assert mutated == True

        config = self.get_config()

        for _ in range(10):
            body = Body.random(config)
            controller = DecentralController(SineController, body, deltaTime=0.2)

            config.mutation.control = body.get_nr_modules()
            res = controller.mutate_maybe(config)
            assert res == True

            allNodes = []
            traverse_get_list(body.root, allNodes)

            individual_likelihood = 1000
            mutated = False
            for i, node in enumerate(allNodes):
                before = str(node.controller)
                if node != body.root:
                    res = node.controller.mutate_maybe(config, individual_likelihood)
                    mutated = mutated or res
                    print("We here", res)

                if i == 0:
                    assert mutated == False
                    assert str(node.controller) == before
                if i >= 1:
                    assert mutated == True
                    print(i, mutated)
                    assert str(node.controller) != before
