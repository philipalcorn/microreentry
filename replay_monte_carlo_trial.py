import argparse
import json
from pathlib import Path

from config import Config
from display import display_result, display_step
from drawing import clear_terminal, hide_cursor, move_cursor_home, show_cursor
from muscles import Muscle
from simulation import run_simulation
from topology import build_sheet


def _load_summary(results_path):
    path = Path(results_path)
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {results_path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Results file is not a JSON object")

    has_hits = isinstance(data.get("hits"), list)
    has_trial_results = isinstance(data.get("trial_results"), list)
    if not has_hits and not has_trial_results:
        raise ValueError(
            "Results file does not look like a Monte Carlo summary with 'hits' or 'trial_results'"
        )

    return data


def _select_hit(summary, hit_index=None, trial_number=None, source="trial_results"):
    records = summary.get(source, [])

    if not records:
        if source == "trial_results":
            records = summary.get("hits", [])
            source = "hits"

    if not records:
        raise ValueError("Results file has no replayable records")

    if trial_number is not None:
        for hit in records:
            if hit.get("trial") == trial_number:
                return hit
        raise ValueError(f"No hit found for trial {trial_number}")

    if hit_index is None:
        hit_index = 0

    if not (0 <= hit_index < len(records)):
        raise IndexError(f"hit_index {hit_index} is out of range (0..{len(records)-1})")

    return records[hit_index]


def _apply_trial_modifications(muscles, hit):
    modifications = hit.get("modifications", [])
    if not modifications:
        raise ValueError("Selected hit has no modifications")

    for mod in modifications:
        muscle_id = mod.get("muscle_id")
        if muscle_id is None or not (0 <= muscle_id < len(muscles)):
            raise ValueError(f"Invalid muscle_id in hit modifications: {muscle_id}")

        rp_value = mod.get("effective_rp", mod.get("randomized_rp"))
        ct_value = mod.get("effective_ct")

        if rp_value is None:
            raise ValueError(f"No RP value found for muscle_id {muscle_id}")

        if ct_value is None:
            ct_value = muscles[muscle_id].default_conduction_time

        muscles[muscle_id].set_individual_defaults(rp=rp_value, ct=ct_value)

        # Keep RP strictly greater than CT for physiologic consistency.
        if muscles[muscle_id].refractory_period <= muscles[muscle_id].conduction_time:
            muscles[muscle_id].refractory_period = muscles[muscle_id].conduction_time + 1
            muscles[muscle_id].default_refractory_period = muscles[muscle_id].refractory_period


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Replay one saved Monte Carlo hit with normal simulation flags"
    )
    parser.add_argument(
        "--results_path",
        type=str,
        required=True,
        help="Path to saved Monte Carlo JSON summary",
    )
    parser.add_argument(
        "--hit_index",
        type=int,
        default=0,
        help="Zero-based index in summary['hits'] (ignored if --trial is provided)",
    )
    parser.add_argument(
        "--trial",
        type=int,
        default=None,
        help="Replay a specific trial number from summary['hits']",
    )
    parser.add_argument(
        "--max_timesteps",
        type=int,
        default=None,
        help="Optional timestep cap for replay run",
    )
    parser.add_argument(
        "--source",
        choices=["trial_results", "hits"],
        default="trial_results",
        help="Which section in the summary to replay from",
    )
    parser.add_argument(
        "--infinite",
        type=str,
        default=None,
        help="Override infinite mode (true/false)",
    )

    args, remaining = parser.parse_known_args(argv)
    cfg = Config.from_args(remaining)

    if args.infinite is not None:
        v = str(args.infinite).strip().lower()
        if v in ("1", "true", "t", "yes", "y", "on"):
            cfg.infinite = True
        elif v in ("0", "false", "f", "no", "n", "off"):
            cfg.infinite = False
        else:
            raise ValueError(
                f"Invalid arg for infinite: '{args.infinite}'. Use true/false or 1/0"
            )

    summary = _load_summary(args.results_path)
    hit = _select_hit(
        summary,
        hit_index=args.hit_index,
        trial_number=args.trial,
        source=args.source,
    )

    nodes, muscles = build_sheet(cfg.length)
    Muscle.set_defaults(muscles, rp=cfg.default_rp, ct=cfg.default_ct)
    Muscle.set_multiplier_for_ids(muscles, cfg.blocked_ids, rp=cfg.slow_rp, ct=cfg.slow_ct)

    _apply_trial_modifications(muscles, hit)

    use_live_display = cfg.graphics or cfg.log

    try:
        if use_live_display:
            hide_cursor()

        result = run_simulation(
            cfg,
            nodes,
            muscles,
            max_timesteps=args.max_timesteps,
            step_callback=(
                (lambda timestep, n, m, micro, event_log: display_step(cfg, timestep, n, m, micro, event_log))
                if use_live_display
                else None
            ),
        )

        if use_live_display:
            move_cursor_home()
            clear_terminal()

        print(f"Replayed trial: {hit.get('trial')}")
        display_result(cfg, result, nodes, muscles)

    finally:
        if use_live_display:
            show_cursor()


if __name__ == "__main__":
    main()
