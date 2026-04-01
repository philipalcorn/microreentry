from nodes import Node
from muscles import Muscle


def get_node_id(r, c, l):
    return r * (l + 1) + c


def build_sheet(l):
    num_nodes = (l + 1) * (l + 1)
    num_muscles = 2 * l * (l + 1)

    nodes = [Node(i) for i in range(num_nodes)]
    muscles = [Muscle(i) for i in range(num_muscles)]

    mid = 0

    # Horizontal muscles
    for r in range(l + 1):
        for c in range(l):
            n1 = get_node_id(r, c, l)
            n2 = get_node_id(r, c + 1, l)

            muscles[mid].connect_node(n1)
            muscles[mid].connect_node(n2)

            nodes[n1].connect_muscle(mid)
            nodes[n2].connect_muscle(mid)

            mid += 1

    # Vertical muscles
    for r in range(l):
        for c in range(l + 1):
            n1 = get_node_id(r, c, l)
            n2 = get_node_id(r + 1, c, l)

            muscles[mid].connect_node(n1)
            muscles[mid].connect_node(n2)

            nodes[n1].connect_muscle(mid)
            nodes[n2].connect_muscle(mid)

            mid += 1

    return nodes, muscles
