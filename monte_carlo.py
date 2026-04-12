"""Monte Carlo helpers for randomized muscle RP/CT experiments.

Example:
    summary = run_muscle_rp_monte_carlo(
        cfg,
        muscle_ids=[12, 24],
        rp_ranges=[(120, 600), (200, 700)],
        ct_ranges=[(2, 20), (4, 24)],
        trials=200,
        max_timesteps=400,
        seed=42,
        save_path="results/monte_carlo_micro_hits.json",
        base_nodes=nodes,
        base_muscles=muscles,
    )
"""

import copy
import json
import random
from pathlib import Path

from topology import build_sheet
from muscles import Muscle
from simulation import run_simulation


def _sample_range(rng, low, high):
    if isinstance(low, int) and isinstance(high, int):
        return rng.randint(low, high)
    return rng.uniform(float(low), float(high))


def display_monte_carlo_summary(summary):
    print()
    print("Monte Carlo summary:")
    print(f" - Target muscle ids: {summary['muscle_ids']}")
    rp_ranges_display = summary.get("rp_ranges_input", summary["rp_ranges"])
    ct_ranges_display = summary.get("ct_ranges_input", summary.get("ct_ranges"))
    print(f" - RP ranges: {rp_ranges_display}")
    if ct_ranges_display is not None:
        print(f" - CT ranges: {ct_ranges_display}")
    print(f" - Trials: {summary['trials']}")
    print(f" - Reentries: {summary['reentry_count']}")
    print(f" - Reentry rate: {summary['reentry_rate']:.3f}")
    if "saved_to" in summary:
        print(f" - Saved results: {summary['saved_to']}")


def run_muscle_rp_monte_carlo(
    cfg,
    muscle_ids,
    rp_ranges,
    ct_ranges=None,
    trials=100,
    max_timesteps=None,
    seed=None,
    save_path=None,
    base_nodes=None,
    base_muscles=None,
):
    """Run repeated simulations while randomizing RP/CT for target muscles.

    Args:
        cfg: A Config instance.
        muscle_ids: Target muscle IDs to modify in each trial.
        rp_ranges: Inclusive (min_rp, max_rp) pairs, one per target muscle.
        ct_ranges: Optional inclusive (min_ct, max_ct) pairs, one per muscle.
            If omitted, CT stays at each muscle's baseline value.
        trials: Number of independent runs.
        max_timesteps: Optional hard cap passed to run_simulation.
        seed: Optional random seed for reproducible randomization.
        save_path: Optional JSON file path where micro-reentry hits are saved.
        base_nodes: Optional baseline nodes copied for each trial.
        base_muscles: Optional baseline muscles copied for each trial.

    Returns:
        Dictionary with summary stats and details for micro-reentry hit trials.
    """
    if trials <= 0:
        raise ValueError("trials must be > 0")
    if not muscle_ids:
        raise ValueError("muscle_ids must not be empty")
    if len(rp_ranges) not in (1, len(muscle_ids)):
        raise ValueError(
            "rp_ranges length must be 1 or match the number of muscle_ids"
        )
    if ct_ranges is not None and len(ct_ranges) not in (1, len(muscle_ids)):
        raise ValueError(
            "ct_ranges length must be 1 or match the number of muscle_ids"
        )

    rp_ranges_expanded = rp_ranges * len(muscle_ids) if len(rp_ranges) == 1 else rp_ranges
    ct_ranges_expanded = None
    if ct_ranges is not None:
        ct_ranges_expanded = ct_ranges * len(muscle_ids) if len(ct_ranges) == 1 else ct_ranges

    for idx, rp_range in enumerate(rp_ranges_expanded):
        if len(rp_range) != 2:
            raise ValueError(f"rp_ranges[{idx}] must be a (min, max) pair")
        rp_min, rp_max = rp_range
        if rp_min > rp_max:
            raise ValueError(f"rp_ranges[{idx}] must be in ascending order")

    if ct_ranges_expanded is not None:
        for idx, ct_range in enumerate(ct_ranges_expanded):
            if len(ct_range) != 2:
                raise ValueError(f"ct_ranges[{idx}] must be a (min, max) pair")
            ct_min, ct_max = ct_range
            if ct_min > ct_max:
                raise ValueError(f"ct_ranges[{idx}] must be in ascending order")

    if (base_nodes is None) != (base_muscles is None):
        raise ValueError("base_nodes and base_muscles must be provided together")

    rng = random.Random(seed)
    micro_hits = []
    trial_results = []

    sim_cfg = copy.deepcopy(cfg)
    sim_cfg.graphics = False
    sim_cfg.log = False
    sim_cfg.debugging = False
    sim_cfg.perf_check = False
    sim_cfg.sim_time = 0

    def validate_muscles(muscles):
        for muscle_id in muscle_ids:
            if not (0 <= muscle_id < len(muscles)):
                raise ValueError(f"muscle_id {muscle_id} is out of range")

    if base_nodes is not None and base_muscles is not None:
        validate_muscles(base_muscles)

    progress_interval = 1000

    for trial in range(1, trials + 1):
        if base_nodes is not None and base_muscles is not None:
            # Each trial starts from the same caller-provided baseline state.
            nodes = copy.deepcopy(base_nodes)
            muscles = copy.deepcopy(base_muscles)
        else:
            nodes, muscles = build_sheet(sim_cfg.length)
            validate_muscles(muscles)
            Muscle.set_defaults(muscles, rp=sim_cfg.default_rp, ct=sim_cfg.default_ct)
            Muscle.set_multiplier_for_ids(
                muscles,
                sim_cfg.blocked_ids,
                rp=sim_cfg.slow_rp,
                ct=sim_cfg.slow_ct,
            )

        trial_modifications = []
        for idx, (muscle_id, rp_range) in enumerate(zip(muscle_ids, rp_ranges_expanded)):
            rp_min, rp_max = rp_range
            randomized_rp = _sample_range(rng, rp_min, rp_max)
            target = muscles[muscle_id]

            if ct_ranges_expanded is not None:
                ct_min, ct_max = ct_ranges_expanded[idx]
                randomized_ct = _sample_range(rng, ct_min, ct_max)
            else:
                randomized_ct = None

            # rp and ct are treated as multipliers of each muscle's default values.
            target.set_multiplier(rp=randomized_rp, ct=randomized_ct)

            trial_modifications.append(
                {
                    "muscle_id": muscle_id,
                    "randomized_rp": randomized_rp,
                    "randomized_ct": randomized_ct,
                    "effective_rp": target.refractory_period,
                    "effective_ct": target.conduction_time,
                }
            )

        result = run_simulation(
            sim_cfg,
            nodes,
            muscles,
            max_timesteps=max_timesteps,
            step_callback=None,
        )

        trial_record = {
            "trial": trial,
            "modifications": trial_modifications,
            "micro": result["micro"],
            "micro_node_id": result["micro_node_id"],
            "timestep": result["timestep"],
            "detection_deadline": result.get("detection_deadline"),
            "detection_timestep": result.get("detection_timestep"),
            "detection_refired_count": result.get("detection_refired_count"),
            "max_refired_before_deadline": result.get("max_refired_before_deadline"),
            "final_refired_count": result.get("final_refired_count"),
            "final_refired_ratio": result.get("final_refired_ratio"),
            "total_nodes": result.get("total_nodes"),
        }
        trial_results.append(trial_record)

        if result["micro"]:
            micro_hits.append(trial_record)

        if trial % progress_interval == 0 or trial == trials:
            print(f"Monte Carlo progress: {trial}/{trials}")

    # Reentry trials first, then non-reentry trials; original trial number preserved.
    trial_results.sort(key=lambda r: (0 if r["micro"] else 1, r["trial"]))

    summary = {
        "trials": trials,
        "reentry_count": len(micro_hits),
        "reentry_rate": len(micro_hits) / trials,
        "muscle_ids": list(muscle_ids),
        "rp_ranges_input": list(rp_ranges),
        "ct_ranges_input": list(ct_ranges) if ct_ranges is not None else None,
        "rp_ranges": [[rp_min, rp_max] for rp_min, rp_max in rp_ranges_expanded],
        "ct_ranges": (
            [[ct_min, ct_max] for ct_min, ct_max in ct_ranges_expanded]
            if ct_ranges_expanded is not None
            else None
        ),
        "seed": seed,
        "trial_results": trial_results,
    }

    if save_path:
        out = Path(save_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        summary["saved_to"] = str(out)

    return summary
