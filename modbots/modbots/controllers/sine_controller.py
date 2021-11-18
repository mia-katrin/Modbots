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
		self.freq = np.random.uniform(-1,1)
		self.phase = np.random.uniform(-1,1)
		self.offset = np.random.uniform(-1,1)

	def advance(self, observation, deltaTime):
		self.state += deltaTime
		return self.amp * math.sin(self.freq * self.state + self.phase) + self.offset

	def reset(self):
		self.state = 0

	def mutate(self):
		rand_choice = ["amp", "freq", "phase", "offset"][np.random.choice([0,1,2,3])]
		to_mutate = "self."+rand_choice
		exec(to_mutate + f"+= {np.random.uniform(-1,1)*0.5}")
		exec(f"{to_mutate} = bounce_back({to_mutate}, SineController.allowable_{rand_choice})")

if __name__ == "__main__":
	d = []
	controller = Controller("hei")
	for i in range(1000):
		d.append(controller.update(.02))
	plt.plot(d)

	plt.figure()
	d = []
	controller.reset()
	controller.mutate()
	for i in range(300):
		d.append(controller.update(.02))
	controller.mutate()
	for i in range(300):
		d.append(controller.update(.02))
	controller.mutate()
	for i in range(300):
		d.append(controller.update(.02))
	controller.mutate()
	for i in range(300):
		d.append(controller.update(.02))
	plt.plot(d)

	plt.figure()
	d = [[],[],[],[]]
	for _ in range(100):
		controller.mutate()
		d[0].append(controller.amp)
		d[1].append(controller.freq)
		d[2].append(controller.phase)
		d[3].append(controller.offset)

	for p in d:
		plt.plot(p)
	plt.show()
