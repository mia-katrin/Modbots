import numpy as np
import matplotlib.pyplot as plt

def sigmoid(i):
    return 1/(1+np.exp(-i)) *2 -1

class Neuron:
    def __init__(self, value=0):
        self.neuron_in = []
        self.weights = []
        self.value = value

    def calc_value(self):
        if len(self.neuron_in) == 0:
            return
        self.value = 0
        for neuron, weight in zip(self.neuron_in, self.weights):
            self.value += neuron.value*weight
        self.value = sigmoid(self.value)

    def __str__(self):
        return str(round(self.value))

class NeuralController:
    def __init__(self):
        pass

    @staticmethod
    def random(layer_limit, node_limit):
        self = NeuralController()

        self.bias = Neuron(value = -1)
        self.input = Neuron()

        self.neurons = [[self.bias, self.input]]

        num_layers = int(np.random.rand()*layer_limit)+1
        for num_layer in range(num_layers):
            layer = [Neuron() for _ in range(int(np.random.rand()*node_limit+1))]
            for neuron in layer:
                neuron.neuron_in = self.neurons[-1]
                neuron.weights = np.random.rand(len(self.neurons[-1]))-0.5
            self.neurons.append(layer)

        self.out = Neuron()
        self.out.neuron_in = self.neurons[-1]
        self.out.weights = np.random.rand(len(self.neurons[-1]))-0.5

        self.neurons.append([self.out])

        return self

    def __call__(self, count):
        self.input.value = count

        for layer in self.neurons:
            for neuron in layer:
                neuron.calc_value()
        return self.out.value

    def mutate(self):
        layer = self.neurons[1+int(np.random.rand()*(len(self.neurons)-2))]
        neuron = layer[int(np.random.rand()*(len(layer)-1))]
        neuron.weights[int(np.random.rand()*(len(neuron.weights)-1))] += np.random.rand()

if __name__ == "__main__":
    for _ in range(20):
        cont = NeuralController.random(3,5)
        a = []
        for e in range(-20,21):
            print(cont(e))
            a.append(cont(e))
        print()
        for layer in cont.neurons:
            print(len(layer))

        plt.plot(a)
    plt.show()
