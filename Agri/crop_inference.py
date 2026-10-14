from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

HIGH_CONFIDENCE = 0.85
MODERATE_CONFIDENCE = 0.70

DISCLAIMER = (
    "This is a machine-learning crop recommendation based on soil N/P/K, pH, "
    "temperature, humidity, and rainfall only. It is not a guarantee of what "
    "should be grown: soil type, irrigation, season, location, and other field "
    "conditions are not in this model."
)


def confidence_band(probability: float, uncertain_threshold: float) -> tuple[str, str]:
    if probability < uncertain_threshold:
        return "uncertain", "uncertain"
    if probability >= HIGH_CONFIDENCE:
        return "high", "certain"
    if probability >= MODERATE_CONFIDENCE:
        return "moderate", "certain"
    return "low", "certain"


def recommendation_text(crop: str, probability: float, level: str, status: str) -> str:
    name = crop.replace("_", " ")
    pct = probability * 100
    if status == "uncertain":
        return (
            f"{name} is the most likely class ({pct:.1f}%), but the calibrated "
            f"confidence is below the decision threshold. Treat this as uncertain "
            f"and compare the top alternatives before acting."
        )
    if level == "high":
        return (
            f"{name} is the strongest match for these soil and climate values "
            f"({pct:.1f}% calibrated confidence)."
        )
    if level == "moderate":
        return (
            f"{name} is the most likely crop, but the model has some uncertainty "
            f"({pct:.1f}% calibrated confidence). Review the alternatives."
        )
    return (
        f"{name} ranks first ({pct:.1f}%), but several classes remain plausible. "
        f"Use the top-3 list rather than a single recommendation."
    )


def choose_uncertain_threshold(y_true: np.ndarray, proba: np.ndarray) -> dict:
    """Pick a threshold from out-of-fold probabilities.

    Prefer 0.60 when it keeps accuracy-when-certain at or above 99% and
    coverage at or above 80%. Otherwise pick the eligible threshold nearest
    to 0.60.
    """
    max_p = proba.max(axis=1)
    pred = proba.argmax(axis=1)
    candidates = [round(t, 2) for t in np.arange(0.40, 0.86, 0.05)]
    rows = []
    for threshold in candidates:
        certain = max_p >= threshold
        coverage = float(certain.mean())
        n_certain = int(certain.sum())
        acc_certain = (
            float((pred[certain] == y_true[certain]).mean()) if n_certain else 0.0
        )
        acc_uncertain = (
            float((pred[~certain] == y_true[~certain]).mean())
            if (~certain).any()
            else None
        )
        rows.append(
            {
                "threshold": threshold,
                "coverage": coverage,
                "n_certain": n_certain,
                "accuracy_when_certain": acc_certain,
                "accuracy_when_uncertain": acc_uncertain,
            }
        )

    eligible = [
        r
        for r in rows
        if r["coverage"] >= 0.80 and r["accuracy_when_certain"] >= 0.99
    ]
    preferred = 0.60
    preferred_row = next((r for r in eligible if r["threshold"] == preferred), None)
    if preferred_row:
        chosen = preferred_row
    elif eligible:
        chosen = min(eligible, key=lambda r: abs(r["threshold"] - preferred))
    else:
        chosen = min(rows, key=lambda r: abs(r["threshold"] - preferred))

    return {
        "uncertain_threshold": chosen["threshold"],
        "selection_rule": (
            "use 0.60 if OOF certain-set accuracy >= 0.99 and coverage >= 0.80; "
            "otherwise nearest eligible threshold; otherwise nearest to 0.60"
        ),
        "chosen": chosen,
        "grid": rows,
    }


def shap_feature_contributions(explainer, X: pd.DataFrame, class_index: int) -> list[dict]:
    values = explainer.shap_values(X, check_additivity=False)
    if isinstance(values, list):
        row = np.asarray(values[class_index])[0]
    else:
        arr = np.asarray(values)
        if arr.ndim == 3:
            # (samples, features, classes) or (samples, classes, features)
            if arr.shape[-1] == X.shape[1]:
                row = arr[0, class_index, :]
            else:
                row = arr[0, :, class_index]
        else:
            row = arr[0]

    contributions = []
    for name, raw in zip(X.columns, row):
        value = float(raw)
        contributions.append(
            {
                "feature": str(name),
                "shap_value": round(value, 6),
                "abs_shap": abs(value),
                "direction": "supports" if value >= 0 else "opposes",
                "bar": int(min(12, round(abs(value) / (max(abs(row)) + 1e-12) * 12))),
            }
        )
    contributions.sort(key=lambda item: item["abs_shap"], reverse=True)
    for item in contributions:
        item.pop("abs_shap", None)
    return contributions


def feature_ranges_from_frame(df: pd.DataFrame, columns: list[str] | None = None) -> dict:
    columns = columns or FEATURE_COLS
    ranges = {}
    for col in columns:
        ranges[col] = {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
        }
    return ranges


def feature_range_warnings(row: dict, ranges: dict) -> list[str]:
    warnings = []
    for col, bounds in ranges.items():
        if col not in row:
            continue
        value = float(row[col])
        low = bounds["min"]
        high = bounds["max"]
        if value < low or value > high:
            warnings.append(
                f"{col}={value:g} is outside the training range "
                f"[{low:.4g}, {high:.4g}]. The model is extrapolating."
            )
    return warnings


def global_importance_factors(importances: np.ndarray, columns: list[str]) -> list[str]:
    order = np.argsort(np.asarray(importances))[::-1]
    return [columns[int(i)] for i in order]


def assemble_crop_prediction(
    *,
    classes: np.ndarray,
    probabilities: np.ndarray,
    uncertain_threshold: float,
    algorithm: str,
    feature_cols: list[str],
    explanations: list[dict] | None,
    fallback_factors: list[str],
    input_warnings: list[str],
    probabilities_calibrated: bool,
) -> dict[str, Any]:
    ranking = sorted(
        zip(classes.tolist(), probabilities.tolist()),
        key=lambda item: item[1],
        reverse=True,
    )
    top_k = [
        {"crop": str(crop), "probability": float(prob)} for crop, prob in ranking[:3]
    ]
    predicted = top_k[0]
    level, status = confidence_band(predicted["probability"], uncertain_threshold)
    explanations = explanations or []
    important = [item["feature"] for item in explanations[:5]] or fallback_factors[:5]
    return {
        "predicted_crop": predicted["crop"],
        "confidence": float(predicted["probability"]),
        "confidence_level": level,
        "status": status,
        "recommendation": recommendation_text(
            predicted["crop"], predicted["probability"], level, status
        ),
        "alternatives": top_k[1:],
        "top_k": top_k,
        "important_factors": important,
        "explanations": explanations,
        "algorithm": algorithm,
        "probabilities_calibrated": probabilities_calibrated,
        "uncertain_threshold": float(uncertain_threshold),
        "features_used": list(feature_cols),
        "input_warnings": input_warnings,
        "disclaimer": DISCLAIMER,
    }
