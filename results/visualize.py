"""Visualize Monte Carlo results as an interactive parallel coordinates plot.

Usage:
    python results/visualize.py [results_json] [--out results.html]

Opens the plot in your browser automatically.
"""

import argparse
import json
import webbrowser
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


def load_dataframe(json_path: Path) -> pd.DataFrame:
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    rows = []
    for rec in summary["trial_results"]:
        row = {
            "micro": int(rec.get("micro", 0)),
            "refired_ratio": rec.get("final_refired_ratio") or 0.0,
            "timestep": rec.get("timestep") or 0,
        }
        for mod in rec["modifications"]:
            mid = mod["muscle_id"]
            row[f"rp_{mid}"] = mod["randomized_rp"]
            if mod.get("randomized_ct") is not None:
                row[f"ct_{mid}"] = mod["randomized_ct"]
        rows.append(row)
    return pd.DataFrame(rows)


def make_parallel_coords(df: pd.DataFrame) -> go.Figure:
    param_cols = [c for c in df.columns if c.startswith("rp_") or c.startswith("ct_")]

    dimensions = []
    for col in param_cols:
        dimensions.append(
            go.parcoords.Dimension(
                label=col,
                values=df[col],
                range=[df[col].min(), df[col].max()],
            )
        )
    # Objective axis last
    dimensions.append(
        go.parcoords.Dimension(
            label="reentry",
            values=df["micro"],
            range=[0, 1],
            tickvals=[0, 1],
            ticktext=["No", "Yes"],
        )
    )

    fig = go.Figure(
        go.Parcoords(
            line=dict(
                color=df["micro"],
                colorscale=[[0, "#1f77b4"], [1, "#d62728"]],
                cmin=0,
                cmax=1,
                showscale=True,
                colorbar=dict(
                    title="Reentry",
                    tickvals=[0, 1],
                    ticktext=["No", "Yes"],
                ),
            ),
            dimensions=dimensions,
        )
    )
    fig.update_layout(
        title="Monte Carlo: muscle parameters vs micro-reentry",
        margin=dict(l=120, r=60, t=100, b=40),
        height=600,
    )
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "json_path",
        nargs="?",
        default="results/monte_carlo_micro_hits.json",
    )
    parser.add_argument("--out", default="results/results.html")
    args = parser.parse_args()

    json_path = Path(args.json_path)
    out_path = Path(args.out)

    print(f"Loading {json_path}...")
    df = load_dataframe(json_path)
    print(f"  {len(df)} trials, {df['micro'].sum()} reentries ({df['micro'].mean():.1%} rate)")

    fig = make_parallel_coords(df)
    fig.write_html(str(out_path), include_plotlyjs="cdn")
    print(f"Saved to {out_path}")
    webbrowser.open(out_path.resolve().as_uri())


if __name__ == "__main__":
    main()
