import numpy as np

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
