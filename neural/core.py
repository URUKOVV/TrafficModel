import random


class Layer:
    TYPE_INPUT = 1
    TYPE_HIDDEN = 2
    TYPE_OUTPUT = 3

    def __init__(self, l_type, count, activation_func=None):
        self.l_type = l_type
        if self.l_type == self.TYPE_HIDDEN:
            self.weights = [random.uniform(0.0, 1.0) for _ in range(0, count)]
        self.activation_func = activation_func
        self.count = count
        self.values = []
        self.results = []
        self.next = None

    def input_values(self, values):
        if self.l_type == self.TYPE_INPUT:
            self.values = values
        else:
            raise ValueError('WRONG TYPE!')

    def set_next_layer(self, layer):
        self.next = layer
