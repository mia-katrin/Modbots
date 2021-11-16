import numpy as np
import matplotlib.pyplot as plt

def sigmoid(i):
    return 1/(1+np.exp(-i)) *2 -1

class Neuron:
    def __init__(self, value=0):
        self.neuron_in = []
        self.weights = []
        self.value = value
        self.bias = -1

    def set_in(self, neurons):
        self.neuron_in = neurons
        self.weights = np.random.rand(len(neurons)+1)-0.5

    def calc_value(self):
        if len(self.neuron_in) == 0:
            return
        self.value = 0
        for neuron, weight in zip(self.neuron_in, self.weights[:-1]):
            self.value += neuron.value*weight
        self.value += self.bias*self.weights[-1]
        self.value = np.tanh(self.value)

    def __str__(self):
        return str(round(self.value))

class NeuralController:
    def __init__(self, layer_limit=3, node_limit=5):
        self.state = 0.0
        self.input = [Neuron(), Neuron(), Neuron()]

        self.neurons = [self.input]

        num_layers = int(np.random.rand()*layer_limit)+1
        for num_layer in range(num_layers):
            layer = [Neuron() for _ in range(int(np.random.rand()*node_limit+1))]
            for neuron in layer:
                neuron.set_in(self.neurons[-1])
            self.neurons.append(layer)

        self.out = Neuron()
        self.out.set_in(self.neurons[-1])

        self.neurons.append([self.out])

    @staticmethod
    def build_from_string(string):
        self = NeuralController(1,1)

        self.input = [Neuron(), Neuron(), Neuron()]
        self.neurons = [self.input]

        layers = string[1:-1].split("|")

        for layer in layers:
            self.neurons.append([])

            weights_in_layer = layer[1:-1].split(")(")

            for neuron_weights in weights_in_layer:

                n = Neuron()
                self.neurons[-1].append(n)
                n.neuron_in = self.neurons[-2]
                for weight in neuron_weights.split(","):
                    n.weights.append(float(weight))

        self.out = self.neurons[-1][0]

        return self

    def __call__(self, obs):
        for i, o in enumerate(obs):
            self.input[i].value = o

        for layer in self.neurons:
            for neuron in layer:
                neuron.calc_value()

        return self.out.value

    def mutate(self):
        layer = self.neurons[1+int(np.random.rand()*(len(self.neurons)-2))]
        neuron = layer[int(np.random.rand()*(len(layer)-1))]
        neuron.weights[int(np.random.rand()*(len(neuron.weights)-1))] += np.random.rand()

    def info_to_str(self):
        info = "["

        for layer in self.neurons[1:]:
            for neuron in layer:
                info += "("
                for weight in neuron.weights:
                    info += str(weight) + ","
                info = info[:-1] + ")"
            info += "|"

        info = info[:-1] + "]"

        return info


if __name__ == "__main__":
    for _ in range(20):
        cont = NeuralController()
        a = []
        for e in np.arange(0.1, 10, 0.1):
            print(cont([e,e,e]))
            a.append(cont([e,e,e]))
        print()
        for layer in cont.neurons:
            print(len(layer))

        plt.plot(a)
    plt.show()
