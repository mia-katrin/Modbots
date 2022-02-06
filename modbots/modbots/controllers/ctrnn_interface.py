import os
import neat
import numpy as np

class CTRNNInterface:
    static_genome_key = 1

    def __init__(self, config="3to1", **kwargs):
        self.kwargs = kwargs
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, f'configs/config-ctrnn-{config}')
        self.config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path)

        self.controllerGenome = neat.genome.DefaultGenome(CTRNNInterface.static_genome_key)
        CTRNNInterface.static_genome_key += 1
        self.controllerGenome.configure_new(self.config.genome_config)
        self.controller = neat.ctrnn.CTRNN.create(self.controllerGenome, self.config, 0.2)

    def prepare_for_evaluation(self):
        self.controller.reset()

    def get_actions(self, observation):
        actions = self.advance(observation[:len(self.controller.input_nodes)], **self.kwargs)
        to_ret = np.pad(
            np.array([actions]),
            ((0, 0), (0, 50 - len(actions))),
            'constant',
            constant_values=0.0
        )
        return to_ret

    def advance(self, observation, advance_time=0.2, time_step=0.2):
        a = self.controller.advance(observation, advance_time, time_step)
        if len(a) == 1:
            return a[0]
        return a

    def reset(self):
        self.controller.reset()

    def mutate(self, config):
        self.controllerGenome.mutate(self.config.genome_config)
        self.controller = neat.ctrnn.CTRNN.create(self.controllerGenome, self.config, config.control.request_period)

    def mutate_maybe(self, config, cont_mut_rate=None) -> bool:
        if cont_mut_rate == None:
            cont_mut_rate = config.mutation.control

        # Recording the performance of the controller:
        obs = [np.random.rand(self.config.genome_config.num_inputs)*1000 for _ in range(1000)]
        self.reset()
        actions = [self.advance(obs[i]) for i in range(1000)]

        # Change values of config to alter mutation probabilities
        self.config.genome_config.conn_add_prob = cont_mut_rate * 0.2
        self.config.genome_config.conn_delete_prob = cont_mut_rate * 0.2
        self.config.genome_config.node_add_prob = cont_mut_rate * 0.2
        self.config.genome_config.node_delete_prob = cont_mut_rate * 0.2

        self.config.genome_config.bias_mutate_rate = cont_mut_rate * 0.8
        self.config.genome_config.activation_mutate_rate = cont_mut_rate * 0.2
        self.config.genome_config.aggregation_mutate_rate = cont_mut_rate * 0.1
        self.config.genome_config.weight_mutate_rate = cont_mut_rate * 0.8
        self.config.genome_config.response_mutate_rate = cont_mut_rate * 0.2
        self.config.genome_config.enabled_mutate_rate = cont_mut_rate * 0.01

        self.config.genome_config.bias_replace_rate = cont_mut_rate * 0.1
        self.config.genome_config.response_replace_rate = cont_mut_rate * 0.1
        self.config.genome_config.weight_replace_rate = cont_mut_rate * 0.1

        self.config.genome_config.bias_mutate_power = config.ea.control_sigma
        self.config.genome_config.response_mutate_power = config.ea.control_sigma
        self.config.genome_config.weight_mutate_power = config.ea.control_sigma

        self.mutate(config)

        # Checking if the performance is the same as it was
        # If not, it's mutated
        self.reset()
        actions2 = [self.advance(obs[i]) for i in range(1000)]
        if np.all(actions == actions2):
            return False
        return True

if __name__ == "__main__":
    cont = CTRNNInterface(config="3to1", advance_time=0.2, time_step=0.2)

    N = 100
    output = np.zeros(N)
    for i in range(N):
        output[i] = cont.advance(np.random.rand(3)*100, 0.2,0.2)

    import matplotlib.pyplot as plt

    plt.plot(output)
    plt.show()
