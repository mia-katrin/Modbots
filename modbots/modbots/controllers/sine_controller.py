import math
import matplotlib.pyplot as plt
import numpy as np

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
		self.freq = np.random.uniform(0.0,6.0)
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

	def mutate(self, config):
		rand_choice = ["amp", "freq", "phase", "offset"][np.random.choice([0,1,2,3])]
		to_mutate = "self."+rand_choice
		exec(to_mutate + f"+= {np.random.uniform(-1,1)*0.2}")
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
