import os
import random

from muscles import Muscle
from config import Config
from topology import build_sheet
from monte_carlo import run_muscle_rp_monte_carlo, display_monte_carlo_summary

# Configuration is managed by Config dataclass:
# sim_time, graphics, infinite, perf_check, heartbeat_time,
# default_ct, default_rp, slow_ct, slow_rp, blocked_ids,
# log, debugging, firing_node, length, max_log_lines.


def main(argv=None):
    cfg = Config.from_args(argv)

    nodes, muscles = build_sheet(cfg.length)

    Muscle.set_defaults(muscles, rp=cfg.default_rp, ct=cfg.default_ct)
    Muscle.set_multiplier_for_ids(muscles, cfg.blocked_ids, rp=cfg.slow_rp, ct=cfg.slow_ct)

    # Monte Carlo setup with explicit per-target ranges.
    mc_target_muscle_ids = [51, 63, 64, 199, 211, 212]

    mc_trials = 50 
    mc_rp_ranges = [
        (0.01, 0.1),  # muscle 51
        #(0.1,0.1),  # muscle 63
        #(0.1,0.1),  # muscle 64
        #(0.1,0.1),  # muscle 199
        #(0.1,0.1),  # muscle 211
        #(0.1,0.1),  # muscle 212
    ]
    #TODO: Need to change the randomizaiton to assign same CT to all muscles
    mc_ct_ranges = [
        (3, 4),  # muscle 51
        #(4,4),  # muscle 63
        #(4,4),  # muscle 64
        #(4,4),  # muscle 199
        #(4,4),  # muscle 211
        #(4,4),  # muscle 212
    ]

    # Randomize each run by default; set MC_SEED for reproducible runs.
    mc_seed_env = os.getenv("MC_SEED")
    mc_seed = int(mc_seed_env) if mc_seed_env is not None else random.randrange(0, 2**32)
    print(f"Monte Carlo seed: {mc_seed}")
    mc_max_timesteps = 500 
    mc_save_path = "results/monte_carlo_micro_hits.json"

    if not all(0 <= mid < len(muscles) for mid in mc_target_muscle_ids):
        raise ValueError(f"mc target muscles {mc_target_muscle_ids} are out of range")

    mc_summary = run_muscle_rp_monte_carlo(
        cfg,
        muscle_ids=mc_target_muscle_ids,
        rp_ranges=mc_rp_ranges,
        ct_ranges=mc_ct_ranges,
        trials=mc_trials,
        max_timesteps=mc_max_timesteps,
        seed=mc_seed,
        save_path=mc_save_path,
        base_nodes=nodes,
        base_muscles=muscles,
    )

    display_monte_carlo_summary(mc_summary)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")

