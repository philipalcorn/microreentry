import time


def log_event(event_log, t, msg, max_log_lines=25):
    for line in event_log:
        if f"Timestep {t}:" in line:
            return
    event_log.append(msg)
    if len(event_log) > max_log_lines:
        event_log.pop(0)


def update_everything(t, nodes, muscles, event_log, micro_origin=None, cfg=None, debugging=False, max_log_lines=25):
    micro = False

    if debugging:
        for m in muscles:
            m.print_stats()

    fire_queue = []

    for m in muscles:
        fired_nodes = m.update(nodes)

        if fired_nodes:
            fire_queue.extend(fired_nodes)
            log_event(event_log, t, f"Timestep {t}: propagation event", max_log_lines=max_log_lines)

        if m.has_fired > 1:
            micro = True

    for nid in fire_queue:
        if 0 <= nid < len(nodes):
            activated, micro_triggers = nodes[nid].fire(muscles)
            if activated:
                log_event(event_log, t, f"Timestep {t}: node {nid} fired", max_log_lines=max_log_lines)

            if micro_triggers:
                micro = True
                if micro_origin is None:
                    micro_origin = micro_triggers[0]

    return t + 1, micro, micro_origin


def run_simulation(
    cfg,
    nodes,
    muscles,
    max_timesteps=None,
    step_callback=None,
):
    event_log = []
    timestep = 0
    nodes[cfg.firing_node].fire(muscles)

    micro = False
    micro_node_id = None
    start = time.perf_counter() if cfg.perf_check else None

    while (not micro) or cfg.infinite:
        if max_timesteps is not None and timestep >= max_timesteps:
            break

        if step_callback:
            step_callback(timestep, nodes, muscles, micro, event_log)

        timestep, micro, micro_node_id = update_everything(
            timestep,
            nodes,
            muscles,
            event_log,
            micro_node_id,
            cfg=cfg,
            debugging=cfg.debugging,
            max_log_lines=cfg.max_log_lines,
        )

        if cfg.heartbeat_time and timestep % cfg.heartbeat_time == 0:
            nodes[cfg.firing_node].fire(muscles)

        if cfg.graphics and cfg.sim_time:
            time.sleep(cfg.sim_time)

    end = time.perf_counter() if cfg.perf_check else None
    elapsed = (end - start) if cfg.perf_check and start is not None and end is not None else None

    return {
        "timestep": timestep,
        "micro": micro,
        "micro_node_id": micro_node_id,
        "event_log": event_log,
        "elapsed": elapsed,
    }
