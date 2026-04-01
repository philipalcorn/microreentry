#!/bin/bash

TRIAL_NUMBER="${1:-1}"
SIM_TIME="${2:-1}"

python3 replay_monte_carlo_trial.py \
	--results_path results/monte_carlo_micro_hits.json \
	--trial "$TRIAL_NUMBER" \
	--source trial_results \
	--graphics true \
	--infinite true \
	--sim_time "$SIM_TIME"
