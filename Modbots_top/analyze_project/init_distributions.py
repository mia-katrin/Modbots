import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

class Node:
    def __init__(self):
        self.children = [None, None, None]

def recurse_add_flat(node, depth, prob):
    if depth > 5:
        return

    for i in range(3):
        if np.random.rand() < prob:
            node.children[i] = Node()
            recurse_add_flat(node.children[i], depth + 1, prob)

def recurse_add_diminishing(node, depth, o_depth, start_prob, diff_prob):
    if depth > 5:
        return

    for i in range(3):
        if np.random.rand() < start_prob - diff_prob*depth/(o_depth-1):
            node.children[i] = Node()
            recurse_add_diminishing(node.children[i], depth + 1, o_depth, start_prob, diff_prob)

def recurse_add_gaussian(node, depth, o_depth, c_mu, c_std):
    if depth > 5:
        return

    for i in range(3):
        if np.random.normal(c_mu, c_std) < (o_depth - depth - 1)/o_depth:
            node.children[i] = Node()
            recurse_add_gaussian(node.children[i], depth + 1, o_depth, c_mu, c_std)

def recurse_count(node):
    count = 1

    for child in node.children:
        if child is not None:
            count += recurse_count(child)

    return count

N_INDS = 100000
N_HIST = 30

def plot_flat():
    probabilities = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]

    counts = []
    for prob in probabilities:
        histogram = np.zeros(N_HIST)
        for _ in tqdm(range(N_INDS)):
            count = 0
            while count < 3:
                root = Node()
                recurse_add_flat(root, 0, prob)
                count = recurse_count(root)
            if count < N_HIST:
                histogram[count] += 1

        counts.append(np.array(histogram) / N_INDS)

    fig, ax = plt.subplots(1)
    for hist, prob in zip(counts, probabilities):
        plt.plot(hist, label=str(prob))
    plt.legend()
    plt.show()

def get_counts_diminishing(pairs):
    counts = []
    for (c_mu, c_std) in pairs:
        histogram = np.zeros(N_HIST)
        for _ in tqdm(range(N_INDS)):
            count = 0
            while count < 3:
                root = Node()
                recurse_add_diminishing(root, 0, 5, c_mu, c_std)
                count = recurse_count(root)
            if count < N_HIST:
                histogram[count] += 1

        counts.append(np.array(histogram) / N_INDS)

    return counts

def plot_flat_diminishing():
    fig, (ax1, ax2) = plt.subplots(1,2, sharey=True)

    p_pairs = [(0.45, 0.45),(0.5, 0.5),(0.55, 0.55),(0.6, 0.6),(0.7, 0.7)]
    for hist, (c_mu, c_std) in zip(get_counts_diminishing(p_pairs), p_pairs):
        ax1.plot(hist, label=str(c_mu) + ", " + str(round(c_mu-c_std, 2)))
    ax1.legend()
    ax1.title.set_text("Varying start probability")

    p_pairs = [(0.5, 0.5),(0.5, 0.4),(0.5, 0.3),(0.5, 0.2),(0.5, 0.1)]
    for hist, (c_mu, c_std) in zip(get_counts_diminishing(p_pairs), p_pairs):
        ax2.plot(hist, label=str(c_mu) + ", " + str(round(c_mu-c_std, 2)))
    ax2.legend()
    ax2.title.set_text("Varying end probability")

    ax1.set_xlabel("Nr Modules")
    ax2.set_xlabel("Nr Modules")
    ax1.set_ylabel("Percentage")

    ax1.set_xticks([i for i in range(0, N_HIST, 3)])
    ax1.set_xticklabels([i for i in range(0, N_HIST, 3)])
    ax2.set_xticks([i for i in range(0, N_HIST, 3)])
    ax2.set_xticklabels([i for i in range(0, N_HIST, 3)])

    plt.show()

def get_counts_gaussian(pairs):
    counts = []
    for (c_mu, c_std) in pairs:
        histogram = np.zeros(N_HIST)
        for _ in tqdm(range(N_INDS)):
            count = 0
            while count < 3:
                root = Node()
                recurse_add_gaussian(root, 0, 5, c_mu, c_std)
                count = recurse_count(root)
            if count < N_HIST:
                histogram[count] += 1

        counts.append(np.array(histogram) / N_INDS)

    return counts

def plot_gaussian():
    fig, (ax1, ax2) = plt.subplots(1,2, sharey=True)

    c_pairs = [(0.75, 0.35), (0.7, 0.35), (0.65, 0.35), (0.6, 0.35), (0.55, 0.35)]
    for hist, (c_mu, c_std) in zip(get_counts_gaussian(c_pairs), c_pairs):
        ax1.plot(hist, label=str(c_mu) + ", " + str(c_std))
    ax1.legend()
    ax1.title.set_text("Varying mu")

    c_pairs = [(0.65, 0.15),(0.65, 0.25),(0.65, 0.35),(0.65, 0.45),(0.65, 0.55)]
    for hist, (c_mu, c_std) in zip(get_counts_gaussian(c_pairs), c_pairs):
        ax2.plot(hist, label=str(c_mu) + ", " + str(c_std))
    ax2.legend()
    ax2.title.set_text("Varying sigma")

    ax1.set_xlabel("Nr Modules")
    ax2.set_xlabel("Nr Modules")
    ax1.set_ylabel("Percentage")

    ax1.set_xticks([i for i in range(0, N_HIST, 3)])
    ax1.set_xticklabels([i for i in range(0, N_HIST, 3)])
    ax2.set_xticks([i for i in range(0, N_HIST, 3)])
    ax2.set_xticklabels([i for i in range(0, N_HIST, 3)])

    plt.show()

def plot_gauss_and_diminishing():
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2, sharey=True, sharex=True)

    gauss_color = [0.267, 0.0048, 0.329]
    dimin_color = [0.187, 0.647, 0.426]

    dim = [1]
    c_pairs = [(0.65, 0.15), (0.6, 0.15), (0.55, 0.15), (0.5, 0.15), (0.45, 0.15)]
    for hist, (c_mu, c_std) in zip(get_counts_gaussian(c_pairs), c_pairs):
        ax1.plot(hist, label=str(c_mu) + ", " + str(c_std), color=gauss_color + dim)
        dim[0] -= 1/len(c_pairs)
    ax1.legend()
    ax1.title.set_text("Varying mu")

    dim = [1]
    c_pairs = [(0.55, 0.15),(0.55, 0.25),(0.55, 0.35),(0.55, 0.45),(0.55, 0.55)]
    for hist, (c_mu, c_std) in zip(get_counts_gaussian(c_pairs), c_pairs):
        ax2.plot(hist, label=str(c_mu) + ", " + str(c_std), color=gauss_color + dim)
        dim[0] -= 1/len(c_pairs)
    ax2.legend()
    ax2.title.set_text("Varying sigma")

    dim = [1]
    p_pairs = [(0.5, 0.5),(0.6, 0.6),(0.7, 0.7),(0.8, 0.8),(0.9,0.9)]
    for hist, (c_mu, c_std) in zip(get_counts_diminishing(p_pairs), p_pairs):
        ax3.plot(hist, label=str(c_mu) + ", " + str(round(c_mu-c_std, 2)), color=dimin_color + dim)
        dim[0] -= 1/len(p_pairs)
    ax3.legend()
    ax3.title.set_text("Varying start probability")

    dim = [1]
    p_pairs = [(0.7, 0.9),(0.7, 0.7),(0.7, 0.5),(0.7, 0.3),(0.7, 0.1)]
    for hist, (c_mu, c_std) in zip(get_counts_diminishing(p_pairs), p_pairs):
        ax4.plot(hist, label=str(c_mu) + ", " + str(round(c_mu-c_std, 2)), color=dimin_color + dim)
        dim[0] -= 1/len(p_pairs)
    ax4.legend()
    ax4.title.set_text("Varying end probability")

    ax3.set_xlabel("Nr Modules")
    ax4.set_xlabel("Nr Modules")
    ax1.set_ylabel("Percentage")
    ax3.set_ylabel("Percentage")

    ax1.set_xticks([i for i in range(0, N_HIST, 3)])
    ax1.set_xticklabels([i for i in range(0, N_HIST, 3)])
    ax2.set_xticks([i for i in range(0, N_HIST, 3)])
    ax2.set_xticklabels([i for i in range(0, N_HIST, 3)])
    ax3.set_xticks([i for i in range(0, N_HIST, 3)])
    ax3.set_xticklabels([i for i in range(0, N_HIST, 3)])
    ax4.set_xticks([i for i in range(0, N_HIST, 3)])
    ax4.set_xticklabels([i for i in range(0, N_HIST, 3)])

    plt.show()

if __name__ == "__main__":
    plot_gauss_and_diminishing()
