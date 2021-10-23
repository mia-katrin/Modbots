import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()

from individual import Individual, Node

DEPTH = 5

def rotx(theta):
    t = theta*np.pi/180
    return np.array([
        [1, 0, 0, 0],
        [0, np.cos(t),-np.sin(t), 0],
        [0, np.sin(t), np.cos(t), 0],
        [0, 0, 0, 1]
    ]).astype(int)

def roty(theta):
    t = theta*np.pi/180
    return np.array([
        [np.cos(t), 0, -np.sin(t), 0],
        [0, 1, 0, 0],
        [np.sin(t), 0, np.cos(t), 0],
        [0, 0, 0, 1]
    ]).astype(int)

def rotz(theta):
    t = theta*np.pi/180
    return np.array([
        [np.cos(t),-np.sin(t), 0, 0],
        [np.sin(t), np.cos(t), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]).astype(int)

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
    index = np.array([DEPTH,(DEPTH-1),(DEPTH-1),1])

    orientation = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    add_ind_recurse(image, ind.genomeRoot, index, orientation)

def get_image_of_pop(pop):
    image = np.zeros((DEPTH*2,DEPTH*2-1,DEPTH*2-1)).astype(int)

    ind = Individual.random(5)

    for ind in pop:
        add_ind(image, ind)

    return image

def hist(image, pop_size):
    h = np.zeros(pop_size+20)

    for elem in image.ravel():
        if elem != 0:
            h[elem] += 1

    return h

def plot_hist(h):
    plt.plot(h)
    plt.show()

def diversity(pop):
    pop_size = len(pop)
    image = get_image_of_pop(pop)
    histogram = hist(image, pop_size)
    return np.sum(histogram)

def test_work():
    ind = Individual()
    ind.genomeRoot = Node("empty")
    ind.genomeRoot.children = [Node("empty"), Node("empty"), Node("empty")]
    ind.genomeRoot.children[1].angle = 90
    ind.genomeRoot.children[1].children = [Node("empty"), Node("empty"), Node("empty")]
    ind.genomeRoot.children[2].angle = 90
    ind.genomeRoot.children[2].children = [Node("empty"), Node("empty"), Node("empty")]
    ind.genomeRoot.children[2].children[2].children = [Node("empty"), None, None]
    ind.genomeRoot.children[2].children[2].children[0].angle = 90
    ind.genomeRoot.children[2].children[2].children[0].children = [Node("empty"), None, None]
    endBoy = ind.genomeRoot.children[2].children[2].children[0].children[0]
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

    add_ind_recurse(image, ind.genomeRoot, index, orientation)

    print(image)
    plot_voxels(image)

def show_random_vs_evolved():
    from evolve import open_population
    # evolved
    pop = open_population(123)
    pop_size = len(pop)

    h = np.array(hist(get_image_of_pop(pop), pop_size))

    plt.figure()
    plt.plot(h, label="evolved")

    # random
    pop_size = 100
    pop = [Individual.random(5) for _ in range(pop_size)]

    h = np.array(hist(get_image_of_pop(pop), pop_size))

    plt.plot(h, label="random")
    plt.legend()
    plt.show()

def plot_voxels(image):
    ax = plt.figure().add_subplot(projection='3d')
    ax.voxels(image, edgecolor='k')

    plt.show()

def show_random_ind():
    ind = Individual.random(5)

    image = get_image_of_pop([ind])
    plot_voxels(image)

if __name__ == "__main__":
    show_random_ind()
