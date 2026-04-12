#!/bin/bash

set -euo pipefail

RESULTS_PATH="results/monte_carlo_micro_hits.json"
SIM_TIME="${1:-0.05}"

TOTAL_TRIALS="$(python3 - <<'PY'
import json
from pathlib import Path

path = Path("results/monte_carlo_micro_hits.json")
data = json.loads(path.read_text(encoding="utf-8"))
print(data["trials"])
PY
)"

echo "Available trials: ${TOTAL_TRIALS} (valid range: 1-${TOTAL_TRIALS})"

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
