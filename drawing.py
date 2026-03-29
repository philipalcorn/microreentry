import sys
from nodes import Node
from muscles import Muscle

RESET = "\033[0m"

# Muscle colors
MUSCLE_REFRACTORY =     "\033[91m"      # red
MUSCLE_READY =          "\033[92m"      # green
MUSCLE_CONDUCTING =     "\033[95m"      # purple

# Node colors
NODE_IDLE =             "\033[96m"      # cyan
NODE_FIRED =            "\033[90m"      # Light Black

# Bars follow muscle color
BAR_READY = MUSCLE_READY
BAR_REFRACTORY = MUSCLE_REFRACTORY
def print_info():
    print("Colors:")
    print(" - Green: Ready muscle")
    print(" - Red: Refractory Period (but no longer conductin) ")
    print(" - Purple: Conducting muscle")
    print(" - Cyan: Node never been fired")
    print(" - Green: Fired node")
    

def move_cursor_home():
    sys.stdout.write("\033[H")
    sys.stdout.flush()


def set_cursor(line, col):
    sys.stdout.write(f"\033[{line};{col}H")
    sys.stdout.flush()


def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def clear_terminal():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def reserve_screen(lines):
    print("\n" * lines, end="")

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


def muscle_color(m):
    if m.is_conducting():
        return MUSCLE_CONDUCTING
    if m.is_refractory():
        return MUSCLE_REFRACTORY
    return MUSCLE_READY


def bar_color(m):
    if m.is_conducting():
        return MUSCLE_CONDUCTING
    if m.is_refractory():
        return BAR_REFRACTORY
    return BAR_READY


def node_color(node):
    return NODE_FIRED if getattr(node, "has_fired", 0) > 0 else NODE_IDLE


def print_sheet(l, nodes, muscles):
    n = l + 1
    total_muscles = 2 * l * (l + 1)
    horiz_count = l * (l + 1)

    id_w = max(2, len(str(total_muscles - 1)))
    node_w = max(4, len(str((l + 1) * (l + 1) - 1)) + 1)
    hmuscle_w = id_w + 6

    def node_str(node):
        color = node_color(node)
        return f"{color}{node.id:>{node_w}}{RESET}"

    def hmuscle_str(muscle):
        color = muscle_color(muscle)
        s = f"---{muscle.id:0{id_w}d}---"
        return f"{color}{s:<{hmuscle_w}}{RESET}"

    def centered(text, width, color):
        return f"{color}{text:^{width}}{RESET}"

    for r in range(n):
        line = ""
        for c in range(n):
            node_idx = r * n + c
            line += node_str(nodes[node_idx])

            if c < n - 1:
                mid = r * l + c
                line += " " + hmuscle_str(muscles[mid]) + " "
        print(line)

        if r < n - 1:
            line = ""
            for c in range(n):
                mid = horiz_count + r * n + c
                line += centered("|", node_w, bar_color(muscles[mid]))
                if c < n - 1:
                    line += " " + " " * hmuscle_w + " "
            print(line)

            line = ""
            for c in range(n):
                mid = horiz_count + r * n + c
                m = muscles[mid]
                line += centered(f"{m.id:0{id_w}d}", node_w, muscle_color(m))
                if c < n - 1:
                    line += " " + " " * hmuscle_w + " "
            print(line)

            line = ""
            for c in range(n):
                mid = horiz_count + r * n + c
                line += centered("|", node_w, bar_color(muscles[mid]))
                if c < n - 1:
                    line += " " + " " * hmuscle_w + " "
            print(line)
