"""Train a Random Forest on Monte Carlo results and visualize diagnostics.
Usage:
    python results/rf_visualize.py [results_json] [--out results_rf.html]

Opens the plot in your browser automatically.
"""

import argparse
import json
import webbrowser
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import cross_val_predict, StratifiedKFold


def load_dataframe(json_path: Path) -> pd.DataFrame:
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    rows = []
    for rec in summary["trial_results"]:
        row = {"micro": int(rec.get("micro", 0))}
        for mod in rec["modifications"]:
            mid = mod["muscle_id"]
            row[f"rp_{mid}"] = mod["randomized_rp"]
            if mod.get("randomized_ct") is not None:
                row[f"ct_{mid}"] = mod["randomized_ct"]
        rows.append(row)
    return pd.DataFrame(rows)


def build_figures(df: pd.DataFrame) -> go.Figure:
    feature_cols = [c for c in df.columns if c.startswith("rp_") or c.startswith("ct_")]
    X = df[feature_cols].values
    y = df["micro"].values

    rf = RandomForestClassifier(n_estimators=400, random_state=42, n_jobs=-1)

    # Cross-validated probabilities for ROC (avoids overfitting artefacts)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    proba_cv = cross_val_predict(rf, X, y, cv=cv, method="predict_proba")[:, 1]

    fpr, tpr, _ = roc_curve(y, proba_cv)
    roc_auc = auc(fpr, tpr)

    # Fit on full data for importances + scatter
    rf.fit(X, y)
    importances = rf.feature_importances_
    order = np.argsort(importances)[::-1]
    sorted_features = [feature_cols[i] for i in order]
    sorted_imp = importances[order]

    # Top-2 features for probability scatter
    top2 = [feature_cols[i] for i in order[:2]]
    proba_full = rf.predict_proba(X)[:, 1]

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[
            "Feature Importances",
            "ROC Curve (5-fold CV)",
            "Reentry Probability Scatter",
            "Predicted Probability Distribution",
        ],
        vertical_spacing=0.18,
        horizontal_spacing=0.12,
    )

    # --- Feature importances ---
    fig.add_trace(
        go.Bar(
            x=sorted_features,
            y=sorted_imp,
            marker_color=[
                "#1f77b4" if f.startswith("rp_") else "#ff7f0e" for f in sorted_features
            ],
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # --- ROC curve ---
    fig.add_trace(
        go.Scatter(
            x=fpr,
            y=tpr,
            mode="lines",
            name=f"AUC = {roc_auc:.3f}",
            line=dict(color="#2ca02c", width=2),
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            line=dict(color="gray", dash="dash"),
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # --- Probability scatter (top 2 features) ---
    fig.add_trace(
        go.Scatter(
            x=df[top2[0]],
            y=df[top2[1]],
            mode="markers",
            marker=dict(
                color=proba_full,
                colorscale=[[0, "#1f77b4"], [1, "#d62728"]],
                cmin=0,
                cmax=1,
                size=5,
                opacity=0.7,
                colorbar=dict(
                    title="P(reentry)",
                    x=1.02,
                    len=0.45,
                    y=0.25,
                ),
            ),
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # --- Probability distribution by class ---
    for label, color, name in [(0, "#1f77b4", "No reentry"), (1, "#d62728", "Reentry")]:
        mask = y == label
        fig.add_trace(
            go.Histogram(
                x=proba_full[mask],
                name=name,
                marker_color=color,
                opacity=0.6,
                nbinsx=30,
                xbins=dict(start=0, end=1, size=1 / 30),
            ),
            row=2,
            col=2,
        )

    # Scatter trace is index 3 (0=bar, 1=roc, 2=roc diagonal, 3=scatter, 4/5=hist)
    scatter_idx = 3

    x_buttons = [
        dict(
            args=[{"x": [df[col].tolist()]}, {"xaxis3.title.text": col}, [scatter_idx]],
            label=col,
            method="update",
        )
        for col in feature_cols
    ]
    y_buttons = [
        dict(
            args=[{"y": [df[col].tolist()]}, {"yaxis3.title.text": col}, [scatter_idx]],
            label=col,
            method="update",
        )
        for col in feature_cols
    ]

    fig.update_layout(
        title="Random Forest: micro-reentry classification",
        height=750,
        margin=dict(l=60, r=80, t=100, b=60),
        barmode="overlay",
        legend=dict(x=0.78, y=0.22),
        updatemenus=[
            dict(
                buttons=x_buttons,
                direction="down",
                showactive=True,
                x=0.02,
                xanchor="left",
                y=0.44,
                yanchor="top",
                bgcolor="white",
                bordercolor="#aaa",
            ),
            dict(
                buttons=y_buttons,
                direction="down",
                showactive=True,
                x=0.24,
                xanchor="left",
                y=0.44,
                yanchor="top",
                bgcolor="white",
                bordercolor="#aaa",
            ),
        ],
    )
    for text, x, y in [("X:", 0.0, 0.435), ("Y:", 0.22, 0.435)]:
        fig.add_annotation(
            text=text,
            x=x, xref="paper", xanchor="right",
            y=y, yref="paper", yanchor="top",
            showarrow=False, font=dict(size=12),
        )

    fig.update_xaxes(title_text="Feature", row=1, col=1, tickangle=-35)
    fig.update_yaxes(title_text="Importance", row=1, col=1)
    fig.update_xaxes(title_text="False Positive Rate", row=1, col=2)
    fig.update_yaxes(title_text="True Positive Rate", row=1, col=2)
    fig.update_xaxes(title_text=top2[0], row=2, col=1)
    fig.update_yaxes(title_text=top2[1], row=2, col=1)
    fig.update_xaxes(title_text="P(reentry)", row=2, col=2)
    fig.update_yaxes(title_text="Count", row=2, col=2)

    return fig, roc_auc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "json_path",
        nargs="?",
        default="results/monte_carlo_micro_hits.json",
    )
    parser.add_argument("--out", default="results/results_rf.html")
    args = parser.parse_args()

    json_path = Path(args.json_path)
    out_path = Path(args.out)

    print(f"Loading {json_path}...")
    df = load_dataframe(json_path)
    print(f"  {len(df)} trials, {df['micro'].sum()} reentries ({df['micro'].mean():.1%} rate)")

    print("Training Random Forest (5-fold CV)...")
    fig, roc_auc = build_figures(df)
    print(f"  ROC AUC: {roc_auc:.3f}")

    fig.write_html(str(out_path), include_plotlyjs="cdn")
    print(f"Saved to {out_path}")
    webbrowser.open(out_path.resolve().as_uri())


if __name__ == "__main__":
    main()
