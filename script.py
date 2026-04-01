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

    # Monte Carlo setup for explicit target muscles.
    mc_target_muscle_ids = [51, 63, 64, 199, 211, 212]  # Example muscle IDs to target in Monte Carlo trials

    mc_trials = 200
    mc_rp_ranges = [(0.005, 4)]  # Same RP range for each target muscle
    mc_ct_ranges = [(0.1, 10)]  # Same CT range for each target muscle

    mc_seed = 42
    mc_max_timesteps = 400
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

