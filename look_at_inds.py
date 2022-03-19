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

FORWARD = np.array([0, 1, 0, 0])

class Scope:

    def __init__(self, parent, node, position, orientation):
        if parent == None:
            self.orientation = orientation
        else:
            self.orientation = orientation @ roty(node.angle)
        self.position = tuple(position)
        self.parent = parent
        self.node = node

    def children(self):
        for node, R in zip(self.node.children, (0, -1, 1)):
            if node is None:
                continue
            orientation = self.orientation @ rotx(90 * R)
            move = (orientation @ FORWARD)[:3].astype(np.int64)
            position = self.position + move
            yield Scope(self.node, node, position, orientation)

    def destroyNode(self):
        C = self.parent.children
        C[C.index(self.node)] = None

def prune_ind(ind):
    root = ind.body.root
    occupied = np.full((40,40,40), False)
    position = np.array([20,20,20])
    orientation = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])

    stack = [Scope(None, root, position, orientation)]
    while stack:
        scope = stack.pop(0)

        if occupied[scope.position] or scope.position[0] < 18:
            scope.destroyNode()
            continue

        stack += list(scope.children())
        occupied[scope.position] = True


"""def place_node(node, occupied, position, orientation):

    move = (orientation @ FORWARD)[:3].astype(np.int64)
    position = position + move

    x, y, z = position
    occupied[x, y, z] += 1
    node.idx = (x, y, z)

    orientation = orientation @ roty(node.angle)

    # Prune Children
    for C, R in zip(node.children, (1, 0, -1)):
        if C:
            place_node(C, occupied, position, orientation @ rotx(90 * R))
            C.parent = node

def prune_nodes(ind):

    occupied = np.full((40,40,40), 0)
    position = np.array([20,20,20])
    orientation = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])
    root = ind.body.root
    place_node(root, occupied, position, orientation)

    bfs = []
    stack = [root]
    while stack:
        node = stack.pop(0)
        bfs.append(node)
        stack += [c for c in node.children if c is not None]

    for node in reversed(bfs):
        x, y, z = node.idx
        if occupied[node.idx] > 1:
            C = node.parent.children
            C[C.index(node)] = None
            occupied[node.idx] -= 1



def prune_ind_node(image, node, index, orientation):
    if node == None:
        return
    print(index)
    # dir = orientation@np.array([0, -1, 0, 1])
    dir = orientation @ FORWARD
    new_index = (index + dir[:3].astype(np.int64)).copy()

    prune_ind_recurse(image, node, new_index, orientation@roty(node.angle))

def prune_ind_recurse(image, node, index, orientation):
    node.image_index = index
    image[index[0], index[1], index[2]] += 1

    # F
    prune_ind_node(image, node.children[0], index, orientation)
    # R
    prune_ind_node(image, node.children[1], index, orientation@rotx(-90))
    # L
    prune_ind_node(image, node.children[2], index, orientation@rotx(90))

def prune_ind(ind):
    image = np.zeros((40,40,40), dtype=np.int64)
    index = np.array([20,20,20])

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
    #for module in reversed(allNodes):
    module = allNodes[-1]
    i = -1
    while module != None:
        x, y, z = module.image_index
        if x > 22 or image[x, y, z] > 1:
            allNodes.remove(module)
            module.parent.children[module.parent.children.index(module)] = None
            image[x, y, z] -= 1

        i -= 1
        if i > -len(allNodes):
            module = allNodes[i]
        else:
            module = None
"""
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
