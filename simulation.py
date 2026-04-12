import time


DETECTION_DEADLINE = 500 


def log_event(event_log, t, msg, max_log_lines=25):
    for line in event_log:
        if f"Timestep {t}:" in line:
            return
    event_log.append(msg)
    if len(event_log) > max_log_lines:
        event_log.pop(0)


def update_everything(
    t,
    nodes,
    muscles,
    event_log,
    micro_origin=None,
    cfg=None,
    debugging=False,
    max_log_lines=25,
):
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

    # Prevent repeated processing when multiple muscles target the same node in one step.
    for nid in set(fire_queue):
        if 0 <= nid < len(nodes):
            activated, _ = nodes[nid].fire(muscles)
            if activated:
                log_event(event_log, t, f"Timestep {t}: node {nid} fired", max_log_lines=max_log_lines)

    # Reentry is detected only if the threshold is crossed by the detection deadline.
    detection_deadline = DETECTION_DEADLINE
    refired_nodes = [node.id for node in nodes if node.has_fired > 1]
    refired_count = len(refired_nodes)
    threshold = len(nodes) / 2 if nodes else 0

    if t < detection_deadline and refired_count > threshold:
        micro = True
        if micro_origin is None and refired_nodes:
            micro_origin = refired_nodes[0]

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
    detection_timestep = None
    detection_refired_count = None
    max_refired_before_deadline = 0
    start = time.perf_counter() if cfg.perf_check else None

    while (not micro) or cfg.infinite:
        if max_timesteps is not None and timestep >= max_timesteps:
            break

        if step_callback:
            step_callback(timestep, nodes, muscles, micro, event_log)

        timestep, step_micro, step_micro_node_id = update_everything(
            timestep,
            nodes,
            muscles,
            event_log,
            micro_node_id,
            cfg=cfg,
            debugging=cfg.debugging,
            max_log_lines=cfg.max_log_lines,
        )

        current_refired_count = sum(1 for node in nodes if node.has_fired > 1)
        if timestep <= DETECTION_DEADLINE:
            max_refired_before_deadline = max(max_refired_before_deadline, current_refired_count)

        # Once reentry is detected, keep it latched for the rest of the run.
        if step_micro:
            if not micro:
                detection_timestep = timestep - 1
                detection_refired_count = current_refired_count
            micro = True
            if micro_node_id is None:
                micro_node_id = step_micro_node_id

        if cfg.heartbeat_time and timestep % cfg.heartbeat_time == 0:
            nodes[cfg.firing_node].fire(muscles)

        if cfg.graphics and cfg.sim_time:
            time.sleep(cfg.sim_time)

    end = time.perf_counter() if cfg.perf_check else None
    elapsed = (end - start) if cfg.perf_check and start is not None and end is not None else None
    final_refired_count = sum(1 for node in nodes if node.has_fired > 1)
    total_nodes = len(nodes)
    final_refired_ratio = (final_refired_count / total_nodes) if total_nodes else 0.0

    return {
        "timestep": timestep,
        "micro": micro,
        "micro_node_id": micro_node_id,
        "detection_deadline": DETECTION_DEADLINE,
        "detection_timestep": detection_timestep,
        "detection_refired_count": detection_refired_count,
        "max_refired_before_deadline": max_refired_before_deadline,
        "final_refired_count": final_refired_count,
        "final_refired_ratio": final_refired_ratio,
        "total_nodes": total_nodes,
        "event_log": event_log,
        "elapsed": elapsed,
    }
