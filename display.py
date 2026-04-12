import time

from drawing import clear_terminal, print_info, print_sheet, set_cursor


def print_sim_stats(cfg):
    blocked_rp = cfg.slow_rp * cfg.default_rp
    blocked_ct = cfg.slow_ct * cfg.default_ct
    if blocked_rp <= blocked_ct:
        blocked_rp = blocked_ct + 1

    print("Timing:")
    print(f" - Default RP: {cfg.default_rp}")
    print(f" - Default CT: {cfg.default_ct}")
    print(f" - Blocked RP modifier: {cfg.slow_rp}")
    print(f" - Blocked CT modifier: {cfg.slow_ct}")
    print(f" - Effective blocked RP: {blocked_rp}")
    print(f" - Effective blocked CT: {blocked_ct}")
    if blocked_rp <= blocked_ct:
        print("(RP>CT constraint was applied to the RP modifier to ensure it is greater than CT)")


def display_step(cfg, timestep, nodes, muscles, micro, event_log):
    clear_terminal()
    set_cursor(1, 1)
    print_info()
    print_sim_stats(cfg)
    if micro:
        print("MICRO DETECTED")
    print(f"Timestep: {timestep}")
    if cfg.graphics:
        print_sheet(cfg.length, nodes, muscles)

    if cfg.log:
        log_row_start = (cfg.length + 1) * 4 + 4
        set_cursor(log_row_start, 1)
        print("Event Log:")
        for i, msg in enumerate(event_log[-cfg.max_log_lines:]):
            set_cursor(log_row_start + 1 + i, 1)
            print(msg)

    if cfg.graphics:
        time.sleep(cfg.sim_time)


def display_result(cfg, result, nodes, muscles):
    print(f"Timestep: {result['timestep']}")
    if result.get("micro"):
        print("Micro detected")
        if result["micro_node_id"] is not None:
            print(f"Micro started by node {result['micro_node_id']}")
    else:
        print("Micro not detected")

    if "final_refired_count" in result and "total_nodes" in result:
        print(
            f"Refired nodes (final): {result['final_refired_count']}/{result['total_nodes']} "
            f"({result.get('final_refired_ratio', 0.0):.3f})"
        )
    if "max_refired_before_deadline" in result and "detection_deadline" in result and "total_nodes" in result:
        print(
            "Max refired nodes before deadline "
            f"t<{result['detection_deadline']}: "
            f"{result['max_refired_before_deadline']}/{result['total_nodes']}"
        )
    if result.get("detection_timestep") is not None:
        print(
            "Detection latched at timestep "
            f"{result['detection_timestep']} "
            f"with {result.get('detection_refired_count')} refired nodes"
        )

    if cfg.perf_check:
        print(f"Elapsed time: {result['elapsed']:.6f} seconds")
    if cfg.graphics:
        print_sheet(cfg.length, nodes, muscles)
    if cfg.log:
        print()
        print("Event Log:")
        for msg in result["event_log"]:
            print(msg)
