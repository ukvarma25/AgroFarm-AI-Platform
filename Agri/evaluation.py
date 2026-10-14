from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)

ROOT = Path(__file__).resolve().parent
PLOTS_DIR = ROOT / "plots"
RESULTS_DIR = ROOT / "results"
PLOTS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)


def evaluate_classifier(y_true, y_pred, y_proba=None, labels=None) -> dict:
    labels = list(labels) if labels is not None else None
    per_class = f1_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    label_names = labels if labels is not None else sorted(set(y_true) | set(y_pred))
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "precision_macro": float(
            precision_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision_weighted": float(
            precision_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "recall_weighted": float(
            recall_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "f1_weighted": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "precision": float(
            precision_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "recall": float(
            recall_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "per_class_f1": {
            str(name): float(score) for name, score in zip(label_names, per_class)
        },
        "confusion_matrix": confusion_matrix(
            y_true, y_pred, labels=labels
        ).tolist(),
        "classification_report": classification_report(
            y_true, y_pred, labels=labels, zero_division=0, output_dict=True
        ),
    }
    if y_proba is not None:
        metrics["n_proba_rows"] = int(len(y_proba))
    return metrics


def summarize_cv_scores(fold_scores: list[dict], keys: list[str]) -> dict:
    summary = {}
    for key in keys:
        values = np.array([fold[key] for fold in fold_scores], dtype=float)
        summary[key] = {
            "mean": float(values.mean()),
            "std": float(values.std(ddof=1) if len(values) > 1 else 0.0),
            "folds": [float(v) for v in values],
        }
    return summary


def evaluate_regressor(y_true, y_pred) -> dict:
    mse = float(mean_squared_error(y_true, y_pred))
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": mse,
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def plot_model_comparison(results_dict: dict, metric_name: str, save_path: str | Path):
    names = list(results_dict.keys())
    values = [results_dict[n][metric_name] for n in names]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(x=names, y=values, ax=ax, hue=names, legend=False, palette="viridis")
    ax.set_ylabel(metric_name.upper())
    ax.set_title(f"Model comparison — {metric_name}")
    ax.set_ylim(min(0, min(values) * 1.1), max(values) * 1.15 if max(values) > 0 else 1)
    for i, v in enumerate(values):
        ax.text(i, v, f"{v:.3f}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(save_path, dpi=140)
    plt.close(fig)


def plot_confusion_matrix(cm, labels, save_path: str | Path):
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        np.array(cm),
        ax=ax,
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        square=False,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion matrix")
    plt.xticks(rotation=75, ha="right", fontsize=7)
    plt.yticks(fontsize=7)
    fig.tight_layout()
    fig.savefig(save_path, dpi=140)
    plt.close(fig)


def save_metrics(results_dict: dict, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
    existing.update(results_dict)
    path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    return existing
