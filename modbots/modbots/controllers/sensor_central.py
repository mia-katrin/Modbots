import numpy as np
import copy

from modbots.util import traverse_get_list
from modbots.controllers.ctrnn_interface import CTRNNInterface

class SensorCentral:
    def __init__(self, body, **kwargs):
        self.kwargs = kwargs
        self.body = body
        self.sensor_control = CopyDecentralController(CTRNNInterface, self.body, **self.kwargs)
        self.central_control = CTRNNInterface(config="15to15")

    def prepare_for_evaluation(self):
        self.sensor_control.prepare_for_evaluation()
        self.central_control.prepare_for_evaluation()

    def _check_lack_of_control(self):
        pass

    def get_actions(self, observation):
        actions = np.zeros((1,50), dtype=float)

        # Run observations through sensor_control
        sensor_processing = self.sensor_control.get_actions(observation)

        # Feed to central_control
        actions = self.central_control.get_actions(sensor_processing)

        return actions

    def mutate(self, config):
        if np.random.rand() < 0.3:
            self.sensor_control.mutate(config)
        else:
            self.central_control.mutate(config)
