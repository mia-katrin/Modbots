import math
import matplotlib.pyplot as plt
import numpy as np
import random

from modbots.util import bounce_back

class SineController():
	allowable_amp = (0.0, 6.0)
	allowable_freq = (0.0, 6.0)
	allowable_phase = (-np.inf, np.inf)
	allowable_offset = (-1, 1)

	def __init__(self, hash="Hei :)"):
		self.nodeid = hash
		self.state = 0.0
		self.amp = np.random.uniform(0.0,1.0)
		self.freq = 3.0
		self.phase = np.random.uniform(-1,1)
		self.offset = np.random.uniform(-1,1)

	def __str__(self):
		string = f"A:{round(self.amp,2)}".ljust(7, " ")
		string += f" F:{round(self.freq,2)}".ljust(8, " ")
		string += f" P:{round(self.phase,2)}".ljust(8, " ")
		string += f" O:{round(self.offset,2)}".ljust(8, " ")
		return string

	def advance(self, observation, deltaTime):
		self.state += deltaTime
		return self.amp * math.sin(self.freq * self.state + self.phase) + self.offset

	def reset(self):
		self.state = 0

	def mutate_maybe(self, config, cont_mut_rate):
		mutated = False

		if np.random.rand() < cont_mut_rate:
			self.amp += random.gauss(0,config.ea.control_sigma)
			mutated = True
		if np.random.rand() < cont_mut_rate:
			self.freq += random.gauss(0,config.ea.control_sigma)
			mutated = True
		if np.random.rand() < cont_mut_rate:
			self.phase += random.gauss(0,config.ea.control_sigma)
			mutated = True
		if np.random.rand() < cont_mut_rate:
			self.offset += random.gauss(0,config.ea.control_sigma)
			mutated = True

		return mutated

	def mutate(self, config):
		rand_choice = ["amp", "freq", "phase", "offset"][np.random.choice([0,1,2,3])]
		to_mutate = "self."+rand_choice
		exec(to_mutate + f"+= {random.gauss(0,config.ea.control_sigma)}")
		exec(f"{to_mutate} = bounce_back({to_mutate}, SineController.allowable_{rand_choice})")

if __name__ == "__main__":
	d = []
	controller = SineController("hei")
	for i in range(100):
		d.append(controller.advance(None, .2))
	plt.plot(d)
	plt.show()

	print(controller)
	controller.mutate(None)
	print(controller)
