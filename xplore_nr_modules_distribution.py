import matplotlib.pyplot as plt
import numpy as np

from individual import Individual

N_INDS = 100000
DEPTH = 5

# Make histogram of robot number of modules
histogram = np.zeros((DEPTH*DEPTH*DEPTH)).astype(np.int32)
for _ in range(N_INDS):
    i = Individual.random(depth=DEPTH).get_nr_expressed_modules()
    histogram[i] += 1

# Find mean number of modules
mean = 0
accumulated = 0
for i in range(len(histogram)):
    accumulated += histogram[i]
    # Having accumulated half of all individuals means we've found the mean
    if accumulated/N_INDS >= 0.5:
        mean = i
        break
print("Gjennomsnitt:", mean)

# Find std
accumulated = 0
for i in range(mean,len(histogram)//2): # We start at the mean
    accumulated += histogram[i]
    # Having accumulated 34.1% of all individuals means we've found the std
    if accumulated/N_INDS >= 0.341:
        print("Standard avvik:", i - mean)
        break

plt.plot(histogram)
plt.show()
