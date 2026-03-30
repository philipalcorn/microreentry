from muscles import Muscle
from nodes import Node
import time
import sys
from config import Config
from drawing import *
from simulation import run_simulation, print_sim_stats

# Configuration is managed by Config dataclass:
# sim_time, graphics, infinite, perf_check, heartbeat_time,
# default_ct, default_rp, slow_ct, slow_rp, blocked_ids,
# log, debugging, firing_node, l, max_log_lines.


def main(argv=None):
    cfg = Config()

    if argv is None:
        argv = sys.argv[1:]

    for arg in argv:
        if "=" not in arg:
            print(f"Unrecognized argument: {arg}")
            exit()
        key, value = arg.split("=", 1)
        key = key.strip().lower()
        value = value.strip()

        if key == "graphics" or key == "g":
            cfg.graphics = value.lower() in ("1", "true", "yes", "y", "t", "on")
        elif key == "infinite" or key == "s":
            cfg.infinite = value.lower() in ("1", "true", "yes", "y", "t", "on")
        elif key == "sim_time" or key == "t":
            try:
                cfg.sim_time = float(value)
            except ValueError:
                pass

    nodes, muscles = build_sheet(cfg.l)

    Muscle.set_defaults(muscles, rp=cfg.default_rp, ct=cfg.default_ct)
    Muscle.set_multiplier_for_ids(muscles, cfg.blocked_ids, rp=cfg.slow_rp, ct=cfg.slow_ct)

    def display_step(timestep, nodes, muscles, micro, event_log):
        clear_terminal()
        set_cursor(1, 1)
        print_info()
        print_sim_stats(cfg)
        if micro:
            print("MICRO DETECTED")
        print(f"Timestep: {timestep}")
        if cfg.graphics:
            print_sheet(cfg.l, nodes, muscles)

        if cfg.log:
            log_row_start = (cfg.l + 1) * 4 + 4
            set_cursor(log_row_start, 1)
            print("Event Log:")
            for i, msg in enumerate(event_log[-cfg.max_log_lines:]):
                set_cursor(log_row_start + 1 + i, 1)
                print(msg)

        if cfg.graphics:
            time.sleep(cfg.sim_time)

    hide_cursor()

    result = run_simulation(
        nodes,
        muscles,
        cfg.firing_node,
        cfg,
        max_timesteps=None,
        step_callback=display_step if cfg.graphics or cfg.log else None,
    )

    move_cursor_home()
    clear_terminal()

    print(f"Timestep: {result['timestep']}")
    print("Micro detected")
    if result["micro_node_id"] is not None:
        print(f"Micro started by node {result['micro_node_id']}")
    if cfg.perf_check:
        print(f"Elapsed time: {result['elapsed']:.6f} seconds")
    if cfg.graphics:
        print_sheet(cfg.l, nodes, muscles)
    if cfg.log:
        print()
        print("Event Log:")
        for msg in result["event_log"]:
            print(msg)

    show_cursor()


if __name__ == "__main__":
    main()

