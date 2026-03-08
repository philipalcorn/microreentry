from muscles import Muscle
from nodes import Node
import time
import sys

RESET = "\033[0m"

# Muscle colors
MUSCLE_READY = "\033[91m"        # red
MUSCLE_CONTRACTING = "\033[93m"  # yellow
MUSCLE_REFRACTORY = "\033[95m"   # pink

# Node colors
NODE_IDLE = "\033[96m"           # cyan
NODE_FIRED = "\033[92m"          # green

# Bars follow muscle color
BAR_READY = MUSCLE_READY
BAR_CONTRACTING = MUSCLE_CONTRACTING
BAR_REFRACTORY = MUSCLE_REFRACTORY

debugging = False

firing_node = 5
l = 12

max_log_lines = 25


blocked_ids = [52, 53, 63, 64, 65, 200, 212, 213, 225, 226]

# defaults in ms converted to timesteps
default_ct = 6
default_contraction = 150
default_rp = 350

# modifiers for selected muscles
slow_ct = 3.33
slow_rp = 0.04

sim_time = 0.01
log = False
def move_cursor_home():
    sys.stdout.write("\033[H")
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
    clear_terminal()

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
    if m.is_contracting():
        return MUSCLE_CONTRACTING
    if m.is_refractory():
        return MUSCLE_REFRACTORY
    return MUSCLE_READY


def bar_color(m):
    if m.is_contracting():
        return BAR_CONTRACTING
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


def log_event(event_log, t, msg):
    for line in event_log:
        if f"Timestep {t}:" in line:
            return
    event_log.append(msg)
    if len(event_log) > max_log_lines:
        event_log.pop(0)


def update_everything(t, nodes, muscles, event_log):
    micro = False

    if debugging:
        for m in muscles:
            m.print_stats()

    for m in muscles:
        if m.update(nodes, muscles):
            log_event(event_log, t, f"Timestep {t}: propagation event")

        if m.has_fired > 1:
            micro = True

    return t + 1, micro


def main():
    event_log = []

    nodes, muscles = build_sheet(l)

    Muscle.set_defaults(
        muscles,
        rp=default_rp,
        ct=default_ct,
        contraction=default_contraction,
    )

    Muscle.set_multiplier_for_ids(
        muscles,
        blocked_ids,
        rp=slow_rp,
        ct=slow_ct,
    )

    # sheet lines + title/log area
    frame_lines = (l + 1) + 3 * l + 6 + max_log_lines

    reserve_screen(frame_lines)
    hide_cursor()

    try:
        t = 0
        nodes[firing_node].fire(muscles)

        micro = False
        while not micro:
            move_cursor_home()

            print(f"Timestep: {t}")
            print_sheet(l, nodes, muscles)
            if log:
                print()
                print("Event Log:")
                for msg in event_log:
                    print(msg)
            for _ in range(max_log_lines - len(event_log)):
                print()

            t, micro = update_everything(t, nodes, muscles, event_log)
            time.sleep(sim_time)

        move_cursor_home()
        print(f"Timestep: {t}")
        print_sheet(l, nodes, muscles)
        if log:
            print()
            print("Event Log:")
            for msg in event_log:
                print(msg)
        #print("Micro detected")

    finally:
        show_cursor()


if __name__ == "__main__":
    main()
