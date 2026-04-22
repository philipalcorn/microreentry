import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from config import Config

RESULTS_PATH = Path(__file__).parent / "monte_carlo_micro_hits.json"

_cfg = Config()
_default_rp = _cfg.default_rp
_default_ct = _cfg.default_ct


def effective_multipliers(rp_mult, ct_mult):
    rp = rp_mult * _default_rp
    ct = ct_mult * _default_ct
    if rp <= ct:
        rp = ct + 1
    return rp / _default_rp, ct / _default_ct


data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

trials = data["trials"]
reentry_count = data["reentry_count"]
reentry_rate = data["reentry_rate"]
muscle_ids = data["muscle_ids"]
seed = data.get("seed")
rp_ranges = data.get("rp_ranges_input", data.get("rp_ranges", []))
ct_ranges = data.get("ct_ranges_input", data.get("ct_ranges"))

print("=" * 52)
print("Monte Carlo Results Summary")
print("=" * 52)
print(f"  Trials:        {trials}")
print(f"  Reentries:     {reentry_count} ({reentry_rate * 100:.1f}%)")
print(f"  Seed:          {seed}")
print(f"  Muscle IDs:    {muscle_ids}")
print(f"  RP ranges:     {rp_ranges}")
if ct_ranges is not None:
    print(f"  CT ranges:     {ct_ranges}")

trial_results = data.get("trial_results", [])
reentries = [r for r in trial_results if r.get("micro")]
non_reentries = [r for r in trial_results if not r.get("micro")]

reentry_trial_nums = [r["trial"] for r in reentries]
print(f"\nReentry trials: {reentry_trial_nums}")

if reentries:
    timesteps = [r["timestep"] for r in reentries]
    ratios = [r["final_refired_ratio"] for r in reentries]
    detection_steps = [r["detection_timestep"] for r in reentries if r.get("detection_timestep") is not None]

    print("\n--- Reentry stats ---")
    print(f"  Avg detection timestep:  {sum(detection_steps) / len(detection_steps):.1f}" if detection_steps else "")
    print(f"  Avg final refired ratio: {sum(ratios) / len(ratios):.3f}")
    print(f"  Min / Max timestep:      {min(timesteps)} / {max(timesteps)}")

print(f"\n{'Trial':>6}  {'Muscles (effective rp mult, cv)':<90}  {'Reentry':>24}")
print("-" * 124)
for r in trial_results:
    label = "yes" if r.get("micro") else "no"
    mods = r.get("modifications", [])
    pairs = "  ".join(
        f"{m['muscle_id']}:({eff_rp:.4f}, {1/eff_ct:.4f})"
        for m in mods
        for eff_rp, eff_ct in [effective_multipliers(m['randomized_rp'], m['randomized_ct'])]
    )
    print(f"{r['trial']:>6}  {pairs:<90}  {label:>7}")
