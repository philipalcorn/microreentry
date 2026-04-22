"""Load Monte Carlo JSON results into an Optuna study and launch the dashboard.

Usage:
    python results/view_optuna.py [results_json] [--port 8080]

Defaults:
    results_json  results/monte_carlo_micro_hits.json
    --port        8080
"""

import argparse
import json
import sys
from pathlib import Path

import optuna
import optuna_dashboard

optuna.logging.set_verbosity(optuna.logging.WARNING)


def load_study(json_path: Path, storage, study_name: str) -> optuna.Study:
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    muscle_ids = summary["muscle_ids"]
    rp_ranges = summary["rp_ranges"]
    ct_ranges = summary.get("ct_ranges")

    distributions: dict[str, optuna.distributions.BaseDistribution] = {}
    for i, mid in enumerate(muscle_ids):
        rp_lo, rp_hi = rp_ranges[i]
        distributions[f"rp_{mid}"] = optuna.distributions.FloatDistribution(rp_lo, rp_hi)
        if ct_ranges:
            ct_lo, ct_hi = ct_ranges[i]
            distributions[f"ct_{mid}"] = optuna.distributions.FloatDistribution(ct_lo, ct_hi)

    study = optuna.create_study(
        study_name=study_name,
        storage=storage,
        direction="maximize",
    )

    trials = []
    for rec in summary["trial_results"]:
        params: dict[str, float] = {}
        for mod in rec["modifications"]:
            mid = mod["muscle_id"]
            params[f"rp_{mid}"] = mod["randomized_rp"]
            if mod.get("randomized_ct") is not None:
                params[f"ct_{mid}"] = mod["randomized_ct"]

        value = rec.get("final_refired_ratio")
        if value is None:
            value = float(rec.get("micro", 0))

        t = optuna.trial.create_trial(
            params=params,
            distributions=distributions,
            value=value,
            state=optuna.trial.TrialState.COMPLETE,
        )
        trials.append(t)

    study.add_trials(trials)

    print(f"Loaded {len(trials)} trials")
    print(f"  Reentry count : {sum(1 for r in summary['trial_results'] if r.get('micro'))}")
    print(f"  Reentry rate  : {summary['reentry_rate']:.3f}")
    return study


def main():
    parser = argparse.ArgumentParser(description="Visualize Monte Carlo results with Optuna dashboard")
    parser.add_argument(
        "json_path",
        nargs="?",
        default="results/monte_carlo_micro_hits.json",
        help="Path to results JSON",
    )
    parser.add_argument("--port", type=int, default=8080, help="Dashboard port (default: 8080)")
    parser.add_argument("--study-name", default="microreentry", help="Optuna study name")
    args = parser.parse_args()

    json_path = Path(args.json_path)
    if not json_path.exists():
        print(f"Error: {json_path} not found", file=sys.stderr)
        sys.exit(1)

    storage = optuna.storages.InMemoryStorage()
    study = load_study(json_path, storage, args.study_name)

    print(f"\nLaunching dashboard at http://localhost:{args.port}")
    print("Press Ctrl+C to stop.\n")
    optuna_dashboard.run_server(storage, host="localhost", port=args.port)


if __name__ == "__main__":
    main()
