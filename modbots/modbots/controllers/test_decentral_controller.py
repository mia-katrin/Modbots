from modbots.controllers.decentral_controller import DecentralController
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

    def test_mutate_maybe(self):
        def true_on_x_func(x, i):
            return i == x

        mutated = False
        for i in range(5):
            res = true_on_x_func(3, i)
            print(res)
            mutated = mutated or res

        assert mutated == True
