import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from mpl_toolkits.mplot3d import Axes3D

from modbots.creature_types.configurable_individual import Individual
from config_util import get_config

config = get_config()

N_INDS = 100
n = 10

def mu_sigma(config):
    # Make histogram of robot number of modules
    histogram = np.zeros((config.individual.ind_depth**3)).astype(np.int32)
    mean = 0
    for _ in tqdm(range(N_INDS)):
        i = Individual.random(config).get_nr_modules()
        histogram[i] += 1

        mean += i
    mean = mean / N_INDS
    print("Gjennomsnitt:", mean)

    # Find std
    std = 0
    for value, count in enumerate(histogram):
        std += (mean - value)**2 * count
    std = np.sqrt(std / N_INDS)
    print("Standard avvik:", std)

    return mean, std

creation_mus = np.linspace(start=0.1, stop=1, num=n)
creation_stds = np.linspace(start=0.6, stop=1, num=n)

mus = []
stds = []

cmus = []
cstds = []

for cmu in creation_mus:
    config.individual.creation_mu = cmu
    for cstd in creation_stds:
        print(cmu, cstd)
        config.individual.creation_std = cstd
        mu, sigma = mu_sigma(config)
        mus.append(mu)
        stds.append(sigma)
        cmus.append(cmu)
        cstds.append(cstd)

# 4D plot

import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = go.Figure(data=[go.Surface(
    x=creation_mus,
    y=creation_stds,
    z=np.array(mus).reshape(n,n),
    surfacecolor=np.array(stds).reshape(n,n))])
fig.update_layout(title_text="Creation mu and std and how they correspond to nr modules")
fig.show()
