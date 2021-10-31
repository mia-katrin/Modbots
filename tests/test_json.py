import json

from individual import Individual

def node_to_list(root):
    queue = [root]
    i = 0

    liste = []
    while len(queue) > 0:
        current = queue.pop(-1)

        liste.append(
            [current.scale, current.angle]
        )
        print(type(i), type(current.scale), type(current.angle))
        for child in current.children:
            if child != None:
                i += 1
                liste[-1].append(i)
                queue.append(child)
            else:
                liste[-1].append(None)

    return liste

"""ind = Individual.random(5)
liste = node_to_list(ind.genomeRoot)"""

liste = [[[1,2,3],[4,5,6]], [1,2,3,4,5,6,7,8]]

jsonfile = json.dumps(liste)

with open('jsonfile.json', 'w') as file:
    file.write(jsonfile)

file = open('jsonfile.json', "r")
obj = json.load(file)
print(obj)
