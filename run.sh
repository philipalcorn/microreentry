#!/bin/bash

set -euo pipefail

# Optional first arg: fixed Monte Carlo seed for reproducibility.
# Example: ./run.sh 123
SEED_ARG="${1:-}"

if [[ -n "$SEED_ARG" ]]; then
	echo "Running Monte Carlo with fixed seed: $SEED_ARG"
	MC_SEED="$SEED_ARG" python3 script.py --graphics false --infinite false --sim_time 0
else
	echo "Running Monte Carlo with random seed"
	python3 script.py --graphics false --infinite false --sim_time 0
fi

echo "Monte Carlo run complete. Results saved to results/monte_carlo_micro_hits.json"
echo "Use ./replay.sh to replay a saved trial"
