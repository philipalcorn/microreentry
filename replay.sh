#!/bin/bash

set -euo pipefail

RESULTS_PATH="results/monte_carlo_micro_hits.json"
SIM_TIME="${1:-0.02}"

read -r TOTAL_TRIALS REENTRY_TRIALS < <(python3 - <<'PY'
import json
from pathlib import Path

data = json.loads(Path("results/monte_carlo_micro_hits.json").read_text(encoding="utf-8"))
reentries = [str(r["trial"]) for r in data.get("trial_results", []) if r.get("micro")]
print(data["trials"], " ".join(reentries))
PY
)

echo "Available trials: ${TOTAL_TRIALS} (valid range: 1-${TOTAL_TRIALS})"
echo "Reentry trials: ${REENTRY_TRIALS}"

while true; do
	read -r -p "Enter trial number: " TRIAL_NUMBER
	if [[ "$TRIAL_NUMBER" =~ ^[0-9]+$ ]] && (( TRIAL_NUMBER >= 1 && TRIAL_NUMBER <= TOTAL_TRIALS )); then
		break
	fi
	echo "Please enter a whole number between 1 and ${TOTAL_TRIALS}."
done

python3 replay_monte_carlo_trial.py \
	--results_path "$RESULTS_PATH" \
	--trial "$TRIAL_NUMBER" \
	--source trial_results \
	--graphics true \
	--infinite true \
	--sim_time "$SIM_TIME"
