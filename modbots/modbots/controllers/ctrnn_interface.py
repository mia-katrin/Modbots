import os
import neat
import numpy as np

class CTRNNInterface:
    static_genome_key = 1

    def __init__(self, central=False, **kwargs):
        self.kwargs = kwargs
        local_dir = os.path.dirname(__file__)
        if central:
            config_path = os.path.join(local_dir, 'config-ctrnn')
        else:
            config_path = os.path.join(local_dir, 'config-ctrnn-3to1')
        self.config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path)

        self.controllerGenome = neat.genome.DefaultGenome(CTRNNInterface.static_genome_key)
        CTRNNInterface.static_genome_key += 1
        self.controllerGenome.configure_new(self.config.genome_config)
        self.controller = neat.ctrnn.CTRNN.create(self.controllerGenome, self.config, 0.02)

    def prepare_for_evaluation(self):
        self.controller.reset()

    def get_actions(self, observation):
        actions = self.advance(observation[:60], **self.kwargs)
        to_ret = np.pad(
            np.array([actions]),
            ((0, 0), (0, 50 - len(actions))),
            'constant',
            constant_values=0.0
        )
        return to_ret

    def advance(self, observation, advance_time=0.02, time_step=0.02):
        a = self.controller.advance(observation, advance_time, time_step)
        if len(a) == 1:
            return a[0]
        return a

    def reset(self):
        self.controller.reset()

    def mutate(self):
        self.controllerGenome.mutate(self.config.genome_config)
        self.controller = neat.ctrnn.CTRNN.create(self.controllerGenome, self.config, 0.02)
