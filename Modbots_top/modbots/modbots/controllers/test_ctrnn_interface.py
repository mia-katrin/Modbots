from modbots.controllers.ctrnn_interface import CTRNNInterface
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

    def test_advance(self):
        cont = CTRNNInterface(config="3to1", advance_time=0.2, time_step=0.2)

        cont.prepare_for_evaluation()
        actions = cont.advance([1,2,3], advance_time=0.2, time_step=0.2)
        assert actions == 0.0

        actions = cont.advance([1,2,3], advance_time=0.2, time_step=0.2)
        assert actions != 0.0

    def test_mutate_maybe(self):
        pass#genome_config = copy.deepcopy(cont.config.genome_config)
