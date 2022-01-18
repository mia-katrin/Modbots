import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from mpl_toolkits.mplot3d import Axes3D

from modbots.creature_types.configurable_individual import Individual
from config_util import get_config

config = get_config()
config.individual.force_interesting = False

N_INDS = 200
n = 20

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

creation_mus = np.linspace(start=0, stop=1, num=n)
creation_stds = np.linspace(start=0, stop=1, num=n)

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

fig = make_subplots(
    rows=1, cols=2,
    specs=[[{'is_3d': True}, {'is_3d': True}]],
    print_grid=False)

fig.append_trace(
    go.Surface(
        x=creation_mus,
        y=creation_stds,
        z=np.array(mus).reshape(n,n),
        surfacecolor=np.array(stds).reshape(n,n)),
    row=1, col=1
)

fig.append_trace(
    go.Surface(
        x=creation_mus,
        y=creation_stds,
        z=np.array(stds).reshape(n,n),
        surfacecolor=np.array(mus).reshape(n,n)),
    row=1, col=2
)

fig.update_layout(
    title="Plot Title",
    scene = dict(
        xaxis_title='Creation mu',
        yaxis_title='Creation std',
        zaxis_title='Nr modules',
    ),
    legend_title="Legend Title",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="RebeccaPurple"
    )
)
fig.show()
