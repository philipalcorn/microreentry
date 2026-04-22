# Micro-Reentry Cardiac Simulation

A computational model of **micro-reentry** — a type of cardiac arrhythmia where an electrical signal gets trapped in a small loop in heart tissue and keeps cycling, rather than dying out normally. This project simulates that behavior on a grid of cardiac cells and uses **Monte Carlo** experiments to discover which tissue parameters make reentry more or less likely.

---

## Table of Contents

1. [Background: What is Micro-Reentry?](#1-background-what-is-micro-reentry)
2. [How the Model Works](#2-how-the-model-works)
3. [Setup: Installing Python and Dependencies](#3-setup-installing-python-and-dependencies)
4. [Viewing the Grid Layout](#4-viewing-the-grid-layout)
5. [Running the Monte Carlo Simulation](#5-running-the-monte-carlo-simulation)
6. [Replaying a Specific Trial](#6-replaying-a-specific-trial)
7. [Visualizing Results](#7-visualizing-results)
8. [Printing a Text Summary of Results](#8-printing-a-text-summary-of-results)
9. [Understanding the Output and Results File](#9-understanding-the-output-and-results-file)
10. [Configuration Parameters Reference](#10-configuration-parameters-reference)
11. [Modifying the Simulation](#11-modifying-the-simulation)
12. [File Overview](#12-file-overview)

---

## 1. Background: What is Micro-Reentry?

In a healthy heart, an electrical signal originates at the sinoatrial (SA) node and spreads outward through cardiac muscle tissue. Each muscle fiber:
1. **Activates** (fires) when the electrical wave reaches it.
2. **Conducts** the signal forward to neighboring tissue.
3. Enters a **refractory period** — a short window where it cannot fire again, no matter how much it is stimulated.

The refractory period is critical: it prevents the signal from doubling back on itself. Once the wave has passed, the tissue it came from is still refractory, so the signal can only travel *forward*.

**Micro-reentry** occurs when the refractory period of a small region is abnormally short. If tissue recovers (becomes excitable again) before the surrounding wavefront has moved far enough away, the signal can loop back and re-excite the same tissue. The result is a self-sustaining loop of electrical activity — an arrhythmia.

This simulation models that process on a two-dimensional grid, and uses statistical experiments to determine the range of tissue parameters (specifically, refractory period length and conduction speed) that leads to reentry.

---

## 2. How the Model Works

### The Grid

The cardiac tissue is represented as a rectangular **grid of nodes and muscles**:

- A **node** represents a junction point in the tissue — think of it as the location where multiple fibers meet.
- A **muscle** (a fiber segment) connects exactly two adjacent nodes and carries the electrical signal between them.

For a grid of side length `L`, there are:
- **(L+1) × (L+1) nodes**, numbered left-to-right, top-to-bottom starting at 0.
- **2 × L × (L+1) muscles**: horizontal muscles first (numbered row by row), then vertical muscles.

The default grid has `L = 12`, giving **169 nodes** and **312 muscles**.

```
Node 0 ---muscle 0--- Node 1 ---muscle 1--- Node 2
  |                     |                     |
muscle 156           muscle 157            muscle 158
  |                     |                     |
Node 13 --muscle 12-- Node 14 --muscle 13-- Node 15
  ...
```

### Nodes

A node is **passive** — it receives a signal and immediately triggers all connected muscles that are not currently in their refractory period (and does not fire back toward the muscle that activated it).

### Muscles

A muscle has two key timing parameters:

| Parameter | Symbol | Default | Meaning |
|-----------|--------|---------|---------|
| **Conduction Time** | CT | ~3.33 timesteps | How long the electrical signal takes to travel through the muscle. The signal arrives at the far node only after this many timesteps. |
| **Refractory Period** | RP | 300 timesteps | How long the muscle stays inactive after firing. It cannot be re-activated until this period expires. |

The essential physiological constraint is: **RP must be greater than CT**. If a muscle's refractory period were shorter than its conduction time, it would reset before the signal even finished passing through — which is physically impossible.

### Simulation Steps

Each **timestep**, the simulation:
1. Advances every active muscle's internal timer by 1.
2. When a muscle's timer reaches its conduction time, it fires its far-end node.
3. Each newly fired node in turn activates all its connected muscles that are ready (not refractory).
4. When a muscle's timer reaches its refractory period, it resets to idle and becomes ready to fire again.

The simulation starts by firing **node 5** (top-left region) and then fires it again every `heartbeat_time` timesteps to represent the regular heartbeat.

### Micro-Reentry Detection

**Reentry is detected** when more than **50% of all nodes** have fired more than once, and this happens *before* the next scheduled heartbeat. This indicates the signal is looping rather than dying out.

### Monte Carlo Experiments

Rather than testing a single configuration, the simulation runs **1,000 independent trials**. In each trial, a selected set of muscles has their refractory period and conduction time randomized within a specified range, and the simulation runs to see whether reentry occurs. After all trials, the results show the statistical relationship between tissue parameters and reentry probability.

---

## 3. Setup: Installing Python and Dependencies

### Prerequisites

You need **Python 3.10 or newer**. To check your version, open a terminal and type:

```bash
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/).

### Installing Required Packages

The core simulation scripts only use Python's standard library and need no additional installation. However, the **visualization script** (`results/visualize.py`) requires two extra packages.

Install them by running:

```bash
pip install pandas plotly
```

If you are using the included virtual environment (`venv/`), activate it first:

```bash
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

Then install:
```bash
pip install pandas plotly
```

### Confirming Everything Works

From the project folder, run:

```bash
python3 view_mesh.py
```

If you see a colored grid of numbers printed in your terminal, the setup is working correctly.

---

## 4. Viewing the Grid Layout

Before running simulations, it helps to see the grid and understand which muscle and node IDs are where.

```bash
python3 view_mesh.py
```

This prints the full 12×12 grid with every node ID and muscle ID labeled in place. Nodes appear as numbers at grid intersections; horizontal muscles appear as `---ID---` labels between nodes; vertical muscles appear as `|` bars with their ID below.

**Options:**

| Option | Example | Effect |
|--------|---------|--------|
| `--length N` | `--length 5` | Change the grid size (default: 12). Use a smaller number like 5 or 6 to see a grid that fits on one screen. |
| `--plain` | `--plain` | Remove color codes — useful if copying the output to a document. |

**Example — small 5×5 grid, no color:**
```bash
python3 view_mesh.py --length 5 --plain
```

Use this view to identify the IDs of the muscles you want to target in the Monte Carlo experiments.

---

## 5. Running the Monte Carlo Simulation

The main simulation is run via `script.py`. The easiest way is through the provided shell script:

```bash
./run.sh
```

This runs 1,000 trials with graphics and display turned off (for speed), and saves results to `results/monte_carlo_micro_hits.json`.

### With a Fixed Seed (Reproducible Results)

If you want the exact same random trials every time — useful for reproducing a specific result for a paper or presentation — pass an integer seed:

```bash
./run.sh 42
```

Any integer will work as the seed. The same seed always produces the same sequence of random trials.

### Running Directly with Python

You can also run `script.py` directly and pass options:

```bash
python3 script.py
```

**Common options:**

| Option | Default | Example | Effect |
|--------|---------|---------|--------|
| `--graphics true` | `false` | `--graphics true` | Show the animated grid in the terminal while simulating. Slows down the run significantly. |
| `--sim_time 0.05` | `0` | `--sim_time 0.05` | Seconds to pause between timesteps when graphics are on. |
| `--length 12` | `12` | `--length 8` | Grid size. |
| `--heartbeat_time 1000` | `1000` | `--heartbeat_time 500` | Timesteps between simulated heartbeats. |
| `--firing_node 5` | `5` | `--firing_node 0` | Which node starts the initial signal. |

**Example — run with the animated display (slower):**
```bash
python3 script.py --graphics true --sim_time 0.05
```

**Example — run headlessly (fastest):**
```bash
python3 script.py --graphics false --sim_time 0
```

### What You Will See

While running (with `--graphics false`), the script prints progress every 1,000 trials:
```
Monte Carlo seed: 2847392918
Monte Carlo progress: 1000/1000

Monte Carlo summary:
 - Target muscle ids: [51, 63, 64, 199, 211, 212]
 - RP ranges: [(0.01, 0.1)]
 - CT ranges: [(3.0, 4.0)]
 - Trials: 1000
 - Reentries: 600
 - Reentry rate: 0.600
 - Saved results: results/monte_carlo_micro_hits.json
```

The results are automatically saved to `results/monte_carlo_micro_hits.json`.

### The Animated Display (When Graphics Are On)

When you run with `--graphics true`, the terminal shows a live view of the grid as the simulation progresses. The color coding is:

| Color | Meaning |
|-------|---------|
| **Green** | Muscle is idle and ready to fire |
| **Purple** | Muscle is actively conducting (signal is traveling through it) |
| **Red** | Muscle is in its refractory period (recently fired, temporarily inactive) |
| **Cyan** | Node has never been fired |
| **Dark/gray** | Node has been fired at least once |

If the display detects reentry, it prints `MICRO DETECTED` at the top of the screen.

---

## 6. Replaying a Specific Trial

After running the Monte Carlo simulation, you can replay any individual trial from the saved results — including watching it animate in the terminal.

The easiest way is the interactive shell script:

```bash
./replay.sh
```

This will:
1. Load the saved results and show you which trials produced reentry.
2. Ask you to type a trial number.
3. Run that trial with a live animated display.

**Example session:**
```
Available trials: 1000 (valid range: 1-1000)
Reentry trials: 7 45 83 101 ...
Enter trial number: 45
```

You can also control the animation speed by passing a delay in seconds:

```bash
./replay.sh 0.05    # 50ms between each timestep (default)
./replay.sh 0.2     # 200ms — slower and easier to watch
./replay.sh 0.01    # 10ms — very fast
```

### Replaying Directly with Python

For more control, use `replay_monte_carlo_trial.py` directly:

```bash
python3 replay_monte_carlo_trial.py \
    --results_path results/monte_carlo_micro_hits.json \
    --trial 45 \
    --graphics true \
    --infinite true \
    --sim_time 0.05
```

**Key options:**

| Option | Example | Effect |
|--------|---------|--------|
| `--results_path PATH` | `--results_path results/monte_carlo_micro_hits.json` | Path to the saved results file (required). |
| `--trial N` | `--trial 45` | Replay trial number N. |
| `--hit_index N` | `--hit_index 0` | Replay the Nth reentry hit (0 = first reentry found). |
| `--infinite true` | `--infinite true` | Keep running the simulation after reentry is detected (so you can watch it loop). |
| `--graphics true/false` | `--graphics true` | Show the animated grid. |
| `--sim_time 0.05` | `--sim_time 0.1` | Seconds between timesteps in the display. |
| `--max_timesteps N` | `--max_timesteps 200` | Stop after N timesteps even if reentry has not been detected. |

**Example — replay the first reentry hit, no animation, just the final result:**
```bash
python3 replay_monte_carlo_trial.py \
    --results_path results/monte_carlo_micro_hits.json \
    --hit_index 0 \
    --graphics false
```

---

## 7. Visualizing Results

Once you have a results file, you can generate an **interactive parallel coordinates plot** that opens automatically in your web browser.

```bash
python3 results/visualize.py
```

Or, specifying a different results file or output location:

```bash
python3 results/visualize.py results/monte_carlo_micro_hits.json --out results/my_plot.html
```

### What the Plot Shows

The plot displays one line per trial. Each vertical axis represents a parameter that was randomized:
- **`rp_N`** — the refractory period multiplier used for muscle N.
- **`ct_N`** — the conduction time multiplier used for muscle N.
- **`reentry`** — whether that trial produced reentry (Yes/No axis on the right).

Lines are colored **blue** for trials with no reentry and **red** for trials where reentry occurred.

**How to use the plot interactively:**
- Click and drag on any vertical axis to select a range. Lines outside that range are hidden, letting you filter to specific parameter combinations.
- Select a range on the `reentry` axis to isolate just the reentry or non-reentry trials.
- Drag a selection on the `rp_N` axis to see which refractory period values correspond to reentry.

This allows you to visually identify the threshold: e.g., "reentry only occurs when the RP multiplier for muscle 211 is below 0.04."

---

## 8. Printing a Text Summary of Results

For a plain-text summary without opening a browser:

```bash
python3 results/print_results.py
```

This reads `results/monte_carlo_micro_hits.json` and prints:

```
====================================================
Monte Carlo Results Summary
====================================================
  Trials:        1000
  Reentries:     600 (60.0%)
  Seed:          2847392918
  Muscle IDs:    [51, 63, 64, 199, 211, 212]
  RP ranges:     [[0.01, 0.1]]
  CT ranges:     [[3.0, 4.0]]

Reentry trials: [7, 45, 83, ...]

--- Reentry stats ---
  Avg detection timestep:  87.3
  Avg final refired ratio: 0.721
  Min / Max timestep:      42 / 499

 Trial  Muscles (effective rp mult, ct mult)           Reentry
------  -------------------------------------------    -------
     7  51:(0.0231, ...)  63:(...)  ...                    yes
    45  ...                                                yes
```

Each row shows the effective parameter multipliers used for that trial, and whether reentry was detected.

---

## 9. Understanding the Output and Results File

The results are saved as a JSON file at `results/monte_carlo_micro_hits.json`. JSON is a plain text format that can be opened in any text editor. The structure is:

```json
{
  "trials": 1000,
  "reentry_count": 600,
  "reentry_rate": 0.6,
  "muscle_ids": [51, 63, 64, 199, 211, 212],
  "rp_ranges_input": [[0.01, 0.1]],
  "ct_ranges_input": [[3.0, 4.0]],
  "seed": 2847392918,
  "trial_results": [
    {
      "trial": 7,
      "micro": true,
      "micro_node_id": 83,
      "timestep": 156,
      "detection_timestep": 87,
      "final_refired_ratio": 0.74,
      "modifications": [
        {
          "muscle_id": 51,
          "randomized_rp": 0.023,
          "randomized_ct": 3.4,
          "effective_rp": 7.0,
          "effective_ct": 11.3
        },
        ...
      ]
    },
    ...
  ]
}
```

**Key fields explained:**

| Field | Meaning |
|-------|---------|
| `trials` | Total number of independent simulations run. |
| `reentry_count` | Number of trials where micro-reentry was detected. |
| `reentry_rate` | Fraction of trials with reentry (0.0 to 1.0). |
| `muscle_ids` | The muscle IDs whose parameters were randomized. |
| `seed` | The random seed used — record this to reproduce the exact same results. |
| `trial` | Trial number (1-indexed). |
| `micro` | `true` if reentry was detected in this trial. |
| `micro_node_id` | The node ID where reentry was first detected. |
| `detection_timestep` | The timestep at which reentry was first flagged. |
| `final_refired_ratio` | Fraction of nodes that fired more than once by simulation end. A higher number means more widespread reentry. |
| `randomized_rp` | The multiplier that was randomly drawn for that muscle's refractory period. |
| `effective_rp` | The actual refractory period (in timesteps) used: `randomized_rp × default_rp`. |
| `effective_ct` | The actual conduction time (in timesteps) used. |

---

## 10. Configuration Parameters Reference

All parameters can be passed as command-line flags to `script.py` or `replay_monte_carlo_trial.py`.

### Simulation Timing

| Parameter | Default | Flag | Description |
|-----------|---------|------|-------------|
| `default_rp` | `300` | — | Default refractory period for all muscles (timesteps). Not a CLI flag; change in `config.py`. |
| `default_ct` | `3.33` | — | Default conduction time for all muscles (timesteps). Not a CLI flag; change in `config.py`. |
| `heartbeat_time` | `1000` | `--heartbeat_time` | Number of timesteps between simulated heartbeats. |
| `sim_time` | `0.05` | `--sim_time` | Seconds to sleep between timesteps (only relevant when graphics are on). |

### Grid

| Parameter | Default | Flag | Description |
|-----------|---------|------|-------------|
| `length` | `12` | `--length` | Side length of the grid. Produces (length+1)² nodes and 2×length×(length+1) muscles. |
| `firing_node` | `5` | `--firing_node` | Node ID that receives the initial electrical signal. |

### Display and Logging

| Parameter | Default | Flag | Description |
|-----------|---------|------|-------------|
| `graphics` | `true` | `--graphics` | Show the animated grid. Set to `false` for maximum speed. |
| `log` | `false` | `--log` | Print a running event log below the grid. |
| `debugging` | `false` | `--debugging` | Print detailed internal state for every muscle at every timestep. Very verbose. |
| `infinite` | `false` | `--infinite` | Keep simulating after reentry is detected instead of stopping. Useful for replaying and watching the loop. |
| `perf_check` | `true` | `--perf_check` | Print elapsed wall-clock time at the end. |

### Monte Carlo Parameters (in `script.py`)

These are set directly in the `script.py` source file rather than as command-line flags:

| Variable | Default | Meaning |
|----------|---------|---------|
| `mc_trials` | `1000` | Number of independent trials to run. |
| `mc_target_muscle_ids` | `[51, 63, 64, 199, 211, 212]` | Muscle IDs whose parameters are randomized each trial. All others stay at their default values. |
| `mc_rp_ranges` | `[(0.01, 0.1)]` | Range of RP multipliers to sample uniformly. `0.1` means the RP is set to 10% of the default. A single range applies to all target muscles. |
| `mc_ct_ranges` | `[(3.0, 4.0)]` | Range of CT multipliers. `4.0` means CT is set to 4× the default. |
| `mc_max_timesteps` | `500` | Maximum timesteps per trial. If reentry is not detected by this point the trial is recorded as no-reentry. |
| `mc_save_path` | `"results/monte_carlo_micro_hits.json"` | Where to save the results. |

---

## 11. Modifying the Simulation

All changes are made by editing `script.py` in any text editor. The relevant section is at the top of the `main()` function.

### Changing the Number of Trials

Find this line and change `1000` to any number:
```python
mc_trials = 1000
```

More trials give more statistically reliable results but take longer to run. 100 trials runs in seconds; 10,000 trials takes a few minutes.

### Changing Which Muscles Are Targeted

```python
mc_target_muscle_ids = [51, 63, 64, 199, 211, 212]
```

Use `python3 view_mesh.py` to see the grid and identify muscle IDs. Muscles near the center of the grid are typically more interesting for reentry studies.

### Changing the Parameter Ranges

```python
mc_rp_ranges = [
    (0.01, 0.1),  # applied to all target muscles
]
mc_ct_ranges = [
    (3.0, 4.0),   # applied to all target muscles
]
```

- The numbers are **multipliers** of each muscle's default values.
- A single range in the list is automatically applied to all target muscles.
- To give each muscle its own range, provide one range per muscle (the list length must match `mc_target_muscle_ids`).

**Example — different ranges per muscle:**
```python
mc_target_muscle_ids = [51, 211]
mc_rp_ranges = [
    (0.01, 0.05),   # muscle 51: very short RP
    (0.05, 0.15),   # muscle 211: moderately short RP
]
mc_ct_ranges = [
    (3.0, 4.0),     # applies to both muscles (single range)
]
```

### Changing the Default Tissue Properties

Open `config.py` and change the values on these lines:
```python
default_ct: float = 10/3     # conduction time in timesteps
default_rp: float = 300      # refractory period in timesteps
```

---

## 12. File Overview

```
microreentry/
├── script.py                    Main entry point — configures and runs Monte Carlo experiments.
├── config.py                    Defines all simulation parameters and parses CLI flags.
├── simulation.py                Core simulation loop (timestep updates, reentry detection).
├── monte_carlo.py               Monte Carlo runner — randomizes parameters over many trials.
├── topology.py                  Builds the node/muscle grid from a given side length.
├── nodes.py                     Node class — receives signals and triggers connected muscles.
├── muscles.py                   Muscle class — conducts signals and enforces refractory period.
├── display.py                   Terminal display — renders the animated grid during replay.
├── drawing.py                   Low-level ANSI terminal drawing functions and color codes.
├── view_mesh.py                 Standalone tool to print the grid with all node/muscle IDs labeled.
├── replay_monte_carlo_trial.py  Replay one trial from saved results, with optional animation.
├── run.sh                       Shell script — easiest way to run the Monte Carlo simulation.
├── replay.sh                    Shell script — interactive prompt to replay a saved trial.
├── tests/
│   └── test_simulation.py       Unit tests for core simulation logic.
└── results/
    ├── monte_carlo_micro_hits.json   Saved Monte Carlo results (created by run.sh / script.py).
    ├── results.html                  Interactive visualization (created by visualize.py).
    ├── visualize.py                  Generates the interactive parallel coordinates plot.
    ├── print_results.py              Prints a plain-text summary of results to the terminal.
    └── rf_visualize.py               Alternate visualization (random forest feature importance).
```

---

## Quick-Start Checklist

For someone running this for the first time:

1. **Install Python 3.10+** if not already installed.
2. **Install visualization dependencies:** `pip install pandas plotly`
3. **Preview the grid:** `python3 view_mesh.py --length 5` to see a small example.
4. **Run the simulation:** `./run.sh` (or `python3 script.py --graphics false`)
5. **View the results interactively:** `python3 results/visualize.py` — a browser window will open.
6. **Print a text summary:** `python3 results/print_results.py`
7. **Watch a reentry trial:** `./replay.sh` and enter a trial number from the reentry list.
