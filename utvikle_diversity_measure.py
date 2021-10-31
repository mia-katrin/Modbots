import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
from skimage.color import hsv2rgb
import seaborn as sns
sns.set_theme()

from individual import Individual, Node

### R and L is likely swapped

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
    index = np.array([DEPTH*2,(DEPTH*2-1),(DEPTH*2-1),1])

    orientation = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    add_ind_recurse(image, ind.genomeRoot, index, orientation)

def get_image_of_pop(pop):
    image = np.zeros((DEPTH*4,DEPTH*4,DEPTH*4)).astype(int)

    ind = Individual.random(5)

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

def plot_hist(image, label=None, elim_0=True):
    bins, counts = np.unique(image, return_counts=True)
    if elim_0:
        counts = counts[1:]
        bins = bins[1:]
    plt.bar(bins, counts, label=label)

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
    plot_voxels(img2, "Accumulated image of a random population")

def plot_voxels(image, title="Plotted voxels"):
    colors = np.where(image == 0, "#000000ff", "#ffffffff")
    hues = ["#000000ff"]
    for i in range(1, int(np.max(image))+1):
        hue = i/(np.max(image)) * 0.9 + 0.1
        rgb = hsv2rgb([[[hue, 1.0, 1.0]]])[0][0]*255
        rgb_hex = [hex(int(elem))[2:] for elem in rgb]
        for j in range(3):
            if len(rgb_hex[j]) == 1:
                rgb_hex[j] = '0' + rgb_hex[j]

        string = f"#{rgb_hex[0]}{rgb_hex[1]}{rgb_hex[2]}88"
        colors[np.where(image == i)] = string

        hues.append(string)

    fig, (ax1, ax2) = plt.subplots(1, 2, gridspec_kw = {'width_ratios':[19, 1]})

    ax = fig.add_subplot(1,2,1, projection='3d')
    ax.voxels(image, facecolors=colors, edgecolor='k')

    cmap = mpl.colors.ListedColormap(hues)
    norm = mpl.colors.Normalize(vmin=0, vmax=np.max(image))
    ax2 = fig.add_subplot(1,2,2)
    cb1 = mpl.colorbar.ColorbarBase(
        ax2, cmap=cmap,
        norm=norm,
        orientation='vertical'
    )
    fig.suptitle(title, fontsize=16)
    plt.show()

def show_random_ind():
    ind = Individual.random(10)

    image = get_image_of_pop([ind])
    plot_voxels(image, "A random individual")

def test_voxel_colors():
    image = np.zeros((50,10,10))
    for i in range(0, 50):
        image[i:50,4:8,1] = i
    plot_voxels(image)

if __name__ == "__main__":
    show_random_ind()
