from modbots.plotting.diversity_measure import get_image_of_pop
from modbots.creature_types.configurable_individual import Individual
from modbots.plotting import plot_voxels

from config_util import get_config
import matplotlib.pyplot as plt
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#sns.set_theme()

from modbots.plotting import plot_voxels, plot_hist

from modbots.creature_types.configurable_individual import Individual
from modbots.creature_types.node import Node
from modbots.util import rotx, roty, rotz

def prune_ind_recurse(image, node, index, orientation):
    node.image_index = index
    image[index[0], index[1], index[2]] += 1

    child = node.children[0] #F
    if child != None:
        dir = orientation@np.array([0, -1, 0, 1])
        new_index = np.ndarray(4)
        new_index[:3] = index[:3] + dir[:3]

        orientationA = orientation@roty(child.angle)
        prune_ind_recurse(image, child, new_index.astype(int), orientationA)

    child = node.children[1] #R
    if child != None:
        orientationR = orientation@rotx(-90)
        dir = orientationR@np.array([0, -1, 0, 1])
        new_index = np.ndarray(4)
        new_index[:3] = index[:3] + dir[:3]

        orientationA = orientationR@roty(child.angle)
        prune_ind_recurse(image, child, new_index.astype(int), orientationA)

    child = node.children[2] #L
    if child != None:
        orientationR = orientation@rotx(90)
        dir = orientationR@np.array([0, -1, 0, 1])
        new_index = np.ndarray(4)
        new_index[:3] = index[:3] + dir[:3]

        orientationA = orientationR@roty(child.angle)
        prune_ind_recurse(image, child, new_index.astype(int), orientationA)

def prune_ind(ind):
    image = np.zeros((40,40,40)).astype(int)
    index = np.array([20,20,20,1])

    orientation = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    prune_ind_recurse(image, ind.body.root, index, orientation)

    # Now everyone has an index. Create the breadth first list

    allNodes = []

    to_process = [ind.body.root]
    while len(to_process) > 0:
        node = to_process.pop(0)
        allNodes.append(node)
        for child in node.children:
            if child != None:
                child.parent = node
                to_process.append(child)

    # Now all nodes are in breadth first list

    # Copied from the C# code and made Python
    module = allNodes[-1]
    i = -1
    while module != None:
        if module.image_index[0] > 22 or image[module.image_index[0], module.image_index[1], module.image_index[2]] > 1:
            allNodes.remove(module);
            module.parent.children[module.parent.children.index(module)] = None
            image[module.image_index[0], module.image_index[1], module.image_index[2]] -= 1

        i -= 1
        if i > -len(allNodes):
            module = allNodes[i]
        else:
            module = None

if __name__ == "__main__":
    config = get_config()
    ind = Individual.random(config)
    ind.body.root.children = [Node(), None, None]
    ind.body.root.children[0].angle = 90
    ind.body.root.children[0].children = [None, None, Node()]
    ind.body.root.children[0].children[2].children = [Node(), None, None]
    ind.body.root.children[0].children[2].children[0].children = [Node(), None, None]
    ind.body.root.children[0].children[2].children[0].children[0].children = [Node(), None, None]
    ind.body.root.children[0].children[2].children[0].children[0].children[0].children = [Node(), None, None]

    path = "remote_results/experiments500/run13350"
    ind = Individual.unpack_ind(path + "/bestInd499", config)

    prune_ind(ind)

    """from modbots.evaluate import get_env, evaluate, close_env, set_env_variables
    set_env_variables(config=config)

    fitness = evaluate(ind, force_evaluate=True, record=False)
    print(f"We got fitness {fitness}")

    close_env()"""

    image = get_image_of_pop([ind])
    plot_voxels(image)
    plt.show()
