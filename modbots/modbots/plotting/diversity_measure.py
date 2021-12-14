import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#sns.set_theme()

from modbots.plotting import plot_voxels, plot_hist

from modbots.creature_types.configurable_individual import Individual
from modbots.creature_types.node import Node
from modbots.util import rotx, roty, rotz

### R and L is likely swapped

def add_ind_recurse(image, node, index, orientation):
    image[index[0], index[1], index[2]] += 1

    child = node.children[0] #F
    if child != None:
        dir = orientation@np.array([0, -1, 0, 1])
        new_index = np.ndarray(4)
        new_index[:3] = index[:3] + dir[:3]

        orientationA = orientation@roty(child.angle)
        add_ind_recurse(image, child, new_index.astype(int), orientationA)

    child = node.children[1] #R
    if child != None:
        orientationR = orientation@rotx(-90)
        dir = orientationR@np.array([0, -1, 0, 1])
        new_index = np.ndarray(4)
        new_index[:3] = index[:3] + dir[:3]

        orientationA = orientationR@roty(child.angle)
        add_ind_recurse(image, child, new_index.astype(int), orientationA)

    child = node.children[2] #L
    if child != None:
        orientationR = orientation@rotx(90)
        dir = orientationR@np.array([0, -1, 0, 1])
        new_index = np.ndarray(4)
        new_index[:3] = index[:3] + dir[:3]

        orientationA = orientationR@roty(child.angle)
        add_ind_recurse(image, child, new_index.astype(int), orientationA)

def add_ind(image, ind):
    index = np.array([10,9,9,1])

    orientation = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    add_ind_recurse(image, ind.body.root, index, orientation)

def get_image_of_pop(pop):
    image = np.zeros((20,20,20)).astype(int)

    for ind in pop:
        add_ind(image, ind)

    return image

def hist(image, pop_size):
    bins, counts = np.unique(image, return_counts=True)

    h = np.zeros(int(bins[-1])+1).astype(int)

    for bin, count in zip(bins, counts):
        if int(bin) != 0:
            h[int(bin)] = count

    return h

def diversity(pop):
    pop_size = len(pop)
    image = get_image_of_pop(pop)
    histogram = hist(image, pop_size)
    return np.sum(histogram)

def test_work():
    ind = Individual()
    ind.bodyRoot = Node("empty")
    ind.bodyRoot.children = [Node("empty"), Node("empty"), Node("empty")]
    ind.bodyRoot.children[1].angle = 90
    ind.bodyRoot.children[1].children = [Node("empty"), Node("empty"), Node("empty")]
    ind.bodyRoot.children[2].angle = 90
    ind.bodyRoot.children[2].children = [Node("empty"), Node("empty"), Node("empty")]
    ind.bodyRoot.children[2].children[2].children = [Node("empty"), None, None]
    ind.bodyRoot.children[2].children[2].children[0].angle = 90
    ind.bodyRoot.children[2].children[2].children[0].children = [Node("empty"), None, None]
    endBoy = ind.bodyRoot.children[2].children[2].children[0].children[0]
    endBoy.angle = 180
    endBoy.children = [Node("empty"), Node("empty"), Node("empty")]
    endBoy.children[2].children = [Node("empty"), None, None]
    endBoy.children[2].children[0].angle = 270
    endBoy.children[2].children[0].children = [Node("empty"), Node("empty"), Node("empty")]
    endBoy.children[2].children[0].children[1].children = [Node("empty"), None, None]
    endBoy.children[2].children[0].children[1].children[0].children = [Node("empty"), None, None]
    cornerBoy = endBoy.children[2].children[0].children[1].children[0].children[0]
    cornerBoy.angle = 90
    cornerBoy.children = [Node("empty"), Node("empty"), Node("empty")]

    index = np.array([5,4,4,1])

    orientation = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    image = np.zeros((10,8,9)).astype(int)

    add_ind_recurse(image, ind.bodyRoot, index, orientation)

    print(image)
    plot_voxels(image)
    plt.show()

def show_random_vs_evolved():
    from evolve import open_population
    # evolved
    pop = open_population(123)
    pop_size = len(pop)

    img = get_image_of_pop(pop)
    h = np.array(hist(img, pop_size))

    plt.figure()
    plot_hist(img, label="evolved")

    # random
    pop_size = 10
    pop = [Individual.random(5) for _ in range(pop_size)]

    img2 = get_image_of_pop(pop)
    h = np.array(hist(img2, pop_size))

    plot_hist(img2, label="random")
    plt.legend()
    plt.title("Histogram of evolved versus random population images")
    plt.xlabel("Bins: Pixel values")
    plt.ylabel("Counts: Pixel value i occured in image")
    plt.show()

    plot_voxels(img, "Accumulated image of an evolved population")
    plt.show()
    plot_voxels(img2, "Accumulated image of a random population")
    plt.show()

def show_random_ind():
    ind = Individual.random(10)

    image = get_image_of_pop([ind])
    plot_voxels(image, "A random individual")
    plt.show()

def test_voxel_colors():
    image = np.zeros((50,10,10))
    for i in range(0, 50):
        image[i:50,4:8,1] = i
    plot_voxels(image)
    plt.show()

if __name__ == "__main__":
    show_random_ind()
