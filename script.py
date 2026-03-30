from muscles import Muscle
from nodes import Node
import time
import sys
from drawing import *


# These settings can be changed by command line args 
#sim_time = 0.5         # Slow
sim_time = 0.05         # Fast    
graphics = True         # Toggle whether or not to draw stuff 
#graphics = False       # Toggle whether or not to draw stuff

perf_check = True
heartbeat_time = 600    # How often the sim attempts to fire the firing node

# defaults in ms converted to timesteps
default_ct = 6 # Default Conduction time
default_rp = 350 # Default Refractory period

# Multipliers for blocked muscles
slow_ct = 4
slow_rp = 0.1
#slow_rp = 1

# The IDs of the muscles to block
blocked_ids = [51,  63, 64, 199, 211, 212 ]
#blocked_ids = []

log = False
debugging = False

firing_node = 5
#firing_node = 31
#firing_node = 162



l = 12 # Size of sheet

max_log_lines = 25 # For the logging stuff 








def print_sim_stats():
    blocked_rp = slow_rp * default_rp
    blocked_ct = slow_ct * default_ct
    if blocked_rp <= blocked_ct:
        blocked_rp = blocked_ct + 1

    print("Timing:")
    print(f" - Default RP: {default_rp}")
    print(f" - Default CT: {default_ct}")
    print(f" - Blocked RP modifier: {slow_rp}")
    print(f" - Blocked CT modifier: {slow_ct}")
    print(f" - Effective blocked RP: {blocked_rp}")
    print(f" - Effective blocked CT: {blocked_ct}")
    if (blocked_rp <= blocked_ct): 
        print("(RP>CT constraint was applied to the RP modifier to ensure it is greater than CT)")


def log_event(event_log, t, msg):
    for line in event_log:
        if f"Timestep {t}:" in line:
            return
    event_log.append(msg)
    if len(event_log) > max_log_lines:
        event_log.pop(0)


def update_everything(t, nodes, muscles, event_log, micro_origin=None):
    micro = False

    if debugging:
        for m in muscles:
            m.print_stats()

    fire_queue = []

    
    # First pass: update muscles and collect node activations
    for m in muscles:
        fired_nodes = m.update(nodes)

        if fired_nodes:
            fire_queue.extend(fired_nodes)
            log_event(event_log, t, f"Timestep {t}: propagation event")

        if m.has_fired > 1:
            micro = True

    # Second pass: apply node firing simultaneously
    for nid in fire_queue:
        if 0 <= nid < len(nodes):
            activated, micro_triggers = nodes[nid].fire(muscles) # Fire the node and check if it was activated, and if any micro triggers were detected
            if activated:
                log_event(event_log, t, f"Timestep {t}: node {nid} fired")

            if micro_triggers and micro_origin is None: # If we detect micro reentry and haven't already set an origin, set it to the first trigger
                micro_origin = micro_triggers[0] # Set the micro reentry origin to the first node that triggered a muscle that fired more than once

    return t + 1, micro, micro_origin


def main(argv=None):
    global graphics, graphics, sim_time

    if argv is None:
        argv = sys.argv[1:]

    for arg in argv:
        if "=" not in arg:
            print(f"Unrecognized argument: {arg}")
        key, value = arg.split("=", 1)
        key = key.strip().lower()
        value = value.strip()

        if key == "graphics":
            graphics = value.lower() in ("1", "true", "yes", "y", "on")
        elif key == "sim_time":
            try:
                sim_time = float(value)
            except ValueError:
                pass

    event_log = []

    nodes, muscles = build_sheet(l)

    Muscle.set_defaults(
        muscles,
        rp=default_rp,
        ct=default_ct,
    )

    Muscle.set_multiplier_for_ids(
        muscles,
        blocked_ids,
        rp=slow_rp,
        ct=slow_ct,
    )

    hide_cursor()

    # main loop
    timestep = 0
    nodes[firing_node].fire(muscles)


    micro = False
    micro_node_id = None
    if perf_check:
        start = time.perf_counter() 

    while not micro:
    #while True:
        clear_terminal()
        
        # go to line 1 to write header and sheet from fixed position
        set_cursor(1, 1)
        print_info()
        print_sim_stats()
        print(f"Timestep: {timestep}")
        if (graphics): 
            print_sheet(l, nodes, muscles)
        # fixed event log area starting directly after sheet
        log_row_start = (l + 1) * 4 + 4
        if log:
            set_cursor(log_row_start, 1)
            print("Event Log:")
            for i, msg in enumerate(event_log[-max_log_lines:]):
                set_cursor(log_row_start + 1 + i, 1)
                print(msg)

        timestep, micro, micro_node_id = update_everything(timestep, nodes, muscles, event_log, micro_node_id)
        if (graphics):
            time.sleep(sim_time)

        if (timestep % heartbeat_time == 0):
            nodes[firing_node].fire(muscles)
    
    # Micro detected here
    
    # Clear Screen
    move_cursor_home()
    clear_terminal()
    if (perf_check):
        end = time.perf_counter()


    print(f"Timestep: {timestep}")
    print("Micro detected")
    if micro_node_id is not None:
        print(f"Micro started by node {micro_node_id}")
    if (perf_check):
        print(f"Elapsed time: {end-start:.6f} seconds")
    if(graphics):
        print_sheet(l, nodes, muscles)
    if log:
        print()
        print("Event Log:")
        for msg in event_log:
            print(msg)

    show_cursor()


if __name__ == "__main__":
    main()

