from copy import deepcopy

def add_count(key, dictionary):
    if key not in dictionary:
        dictionary[key] = 0
    dictionary[key] += 1

def connection_equality(conn, mut, story):
    if conn.key[0] != mut.key[0] or conn.key[1] != mut.key[1]:
        raise Exception("This is not how you use this function! Keys must match")

    if conn.weight != mut.weight:
        add_count("Weight", story)
    if conn.enabled != mut.enabled:
        add_count("Enabled" if mut.enabled else "Disabled", story)

def node_equality(node, mut, story):
    if node.key != mut.key:
        raise Exception("This is not how you use this function! Keys must match")

    if node.bias != mut.bias:
        add_count("Bias", story)
    if node.response != mut.response:
        add_count("Response", story)
    if node.activation != mut.activation:
        add_count(f"Activation {mut.activation}", story)
    if node.aggregation != mut.aggregation:
        add_count(f"Aggregation {mut.aggregation}", story)

def connection_story(connections, connections_mut, story):
    for key, conn in connections_mut.items():
        if key not in connections.keys():
            add_count(f"Connection added", story)
        else:
            connection_equality(connections[key], conn, story)

    for key, conn in connections.items():
        if key not in connections_mut.keys():
            add_count(f"Connection removed", story)

def node_story(nodes, nodes_mut, story):
    for key, node in nodes_mut.items():
        if key not in nodes.keys():
            add_count("Node added", story)
        else:
            node_equality(nodes[key], node, story)

    for key, conn in nodes.items():
        if key not in nodes_mut.keys():
            add_count("Node removed", story)

def mutation_story(cont_deepcopy, cont_mut):
    story = {}

    connection_story(
        cont_deepcopy.controllerGenome.connections,
        cont_mut.controllerGenome.connections,
        story
    )
    node_story(
        cont_deepcopy.controllerGenome.nodes,
        cont_mut.controllerGenome.nodes,
        story
    )

    return story

if __name__ == "__main__":
    # Setup: Get a ctrnn_interface
    from modbots.controllers.ctrnn_interface import CTRNNInterface
    cont = CTRNNInterface(config="3to1")

    config = get_config()
    config.mutation.control = 0.01

    ### Pattern on how to use this

    cont_deepcopy = deepcopy(cont)

    cont.mutate_maybe(config, config.mutation.control)

    changes = mutation_story(cont_deepcopy, cont)
    print(changes)

    ### Pattern stop
