from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesClassifier,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from crop_inference import (
    FEATURE_COLS,
    choose_uncertain_threshold,
    feature_ranges_from_frame,
)
from evaluation import (
    PLOTS_DIR,
    RESULTS_DIR,
    ROOT,
    evaluate_classifier,
    evaluate_regressor,
    plot_confusion_matrix,
    plot_model_comparison,
    save_metrics,
    summarize_cv_scores,
)

DATASETS = ROOT / "datasets"
MODELS = ROOT / "saved_models"
MODELS.mkdir(exist_ok=True)

YIELD_SOURCE = Path(r"C:\Users\Harinath\Downloads\crop_yield 2.csv")
YIELD_SAMPLE_ROWS = 40_000
RANDOM_STATE = 42


def _best_by(results: dict, metric: str, higher_is_better: bool = True) -> str:
    key = max if higher_is_better else min
    return key(results, key=lambda name: results[name][metric])


RF_CROP_PARAMS = {
    "n_estimators": 500,
    "max_depth": None,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "max_features": "sqrt",
    "bootstrap": True,
    "class_weight": None,
    "random_state": RANDOM_STATE,
    "n_jobs": -1,
}

CV_METRIC_KEYS = [
    "accuracy",
    "balanced_accuracy",
    "precision_macro",
    "recall_macro",
    "f1_macro",
    "f1_weighted",
]


def _crop_candidate_models() -> dict:
    return {
        "random_forest": RandomForestClassifier(**RF_CROP_PARAMS),
        "random_forest_balanced": RandomForestClassifier(
            **{**RF_CROP_PARAMS, "class_weight": "balanced"}
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=500,
            max_features="sqrt",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "svm": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "clf",
                    SVC(
                        kernel="rbf",
                        C=2.0,
                        gamma="scale",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "logistic_regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=4000,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
    }


def train_crop_recommendation() -> dict:
    df = pd.read_csv(DATASETS / "crop_recommendation.csv")
    feature_cols = list(FEATURE_COLS)
    X = df[feature_cols]
    y = df["label"].astype(str)

    label_encoder = LabelEncoder()
    y_enc = label_encoder.fit_transform(y)
    labels = list(label_encoder.classes_)
    class_counts = {str(k): int(v) for k, v in y.value_counts().items()}

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    candidates = _crop_candidate_models()
    cv_folds: dict[str, list[dict]] = {name: [] for name in candidates}
    oof_proba = np.zeros((len(y_enc), len(labels)), dtype=float)

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y_enc), start=1):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y_enc[train_idx], y_enc[val_idx]
        y_true_names = label_encoder.inverse_transform(y_val)
        for name, template in candidates.items():
            print(f"[crop] fold {fold}/5 training {name}...")
            model = clone(template)
            model.fit(X_train, y_train)
            pred = model.predict(X_val)
            pred_names = label_encoder.inverse_transform(pred)
            proba = (
                model.predict_proba(X_val)
                if hasattr(model, "predict_proba")
                else None
            )
            if name == "random_forest":
                oof_proba[val_idx] = proba
            metrics = evaluate_classifier(
                y_true_names, pred_names, proba, labels=labels
            )
            cv_folds[name].append(
                {key: metrics[key] for key in CV_METRIC_KEYS}
            )

    cv_summary = {
        name: summarize_cv_scores(folds, CV_METRIC_KEYS)
        for name, folds in cv_folds.items()
    }

    oof_pred = oof_proba.argmax(axis=1)
    oof_true_names = label_encoder.inverse_transform(y_enc)
    oof_pred_names = label_encoder.inverse_transform(oof_pred)
    oof_metrics = evaluate_classifier(
        oof_true_names, oof_pred_names, oof_proba, labels=labels
    )
    threshold_info = choose_uncertain_threshold(y_enc, oof_proba)

    print("[crop] fitting calibrated Random Forest on all data...")
    calibrated = CalibratedClassifierCV(
        estimator=RandomForestClassifier(**RF_CROP_PARAMS),
        method="sigmoid",
        cv=skf,
        ensemble=False,
        n_jobs=-1,
    )
    calibrated.fit(X, y_enc)

    bundle = {
        "model": calibrated,
        "label_encoder": label_encoder,
        "algorithm": "random_forest",
        "feature_cols": feature_cols,
        "labels": labels,
        "task": "crop_recommendation",
        "uncertain_threshold": threshold_info["uncertain_threshold"],
        "threshold_selection": threshold_info["selection_rule"],
        "probabilities_calibrated": True,
        "calibration_method": "sigmoid",
        "feature_ranges": feature_ranges_from_frame(df, feature_cols),
        "rf_hyperparameters": RF_CROP_PARAMS,
    }
    joblib.dump(bundle, MODELS / "crop_model.pkl")

    comparison = {
        name: {
            "accuracy": summary["accuracy"]["mean"],
            "precision": summary["precision_macro"]["mean"],
            "recall": summary["recall_macro"]["mean"],
            "f1": summary["f1_macro"]["mean"],
            "f1_macro": summary["f1_macro"]["mean"],
            "f1_weighted": summary["f1_weighted"]["mean"],
            "balanced_accuracy": summary["balanced_accuracy"]["mean"],
        }
        for name, summary in cv_summary.items()
    }
    for metric in ("accuracy", "f1_macro", "balanced_accuracy"):
        plot_model_comparison(
            comparison, metric, PLOTS_DIR / f"crop_{metric}_comparison.png"
        )
    plot_confusion_matrix(
        oof_metrics["confusion_matrix"],
        labels,
        PLOTS_DIR / "crop_confusion_matrix.png",
    )

    rf_acc = cv_summary["random_forest"]["accuracy"]
    rf_f1 = cv_summary["random_forest"]["f1_macro"]
    print(
        f"[crop] Random Forest 5-fold CV accuracy="
        f"{rf_acc['mean']:.4f} ± {rf_acc['std']:.4f}, "
        f"macro F1={rf_f1['mean']:.4f} ± {rf_f1['std']:.4f}"
    )
    print(
        f"[crop] uncertain threshold="
        f"{threshold_info['uncertain_threshold']:.2f} "
        f"(kept RF without class_weight='balanced')"
    )

    slim = {
        "best_algorithm": "random_forest",
        "n_samples": int(len(df)),
        "n_classes": len(labels),
        "classes": labels,
        "class_counts": class_counts,
        "feature_cols": feature_cols,
        "cv": {
            "n_splits": 5,
            "strategy": "StratifiedKFold",
            "shuffle": True,
            "random_state": RANDOM_STATE,
        },
        "cv_summary": cv_summary,
        "oof_metrics": {
            key: oof_metrics[key]
            for key in (
                "accuracy",
                "balanced_accuracy",
                "precision_macro",
                "recall_macro",
                "f1_macro",
                "f1_weighted",
                "per_class_f1",
            )
        },
        "uncertain_threshold": threshold_info["uncertain_threshold"],
        "threshold_grid": threshold_info["grid"],
        "threshold_selection": threshold_info["selection_rule"],
        "probabilities_calibrated": True,
        "calibration_method": "sigmoid",
        "rf_hyperparameters": {k: v for k, v in RF_CROP_PARAMS.items() if k != "n_jobs"},
        "class_weight": None,
        "caveat": (
            "Cross-validated accuracy describes performance on this 7-feature "
            "dataset. It is not a real-world guarantee of agronomic suitability."
        ),
        "algorithms": comparison,
    }
    return slim


def _load_yield_frame() -> pd.DataFrame:
    sample_path = DATASETS / "yield_sample.csv"
    if sample_path.exists():
        return pd.read_csv(sample_path)

    if not YIELD_SOURCE.exists():
        raise FileNotFoundError(
            f"Yield dataset not found at {YIELD_SOURCE}. Place crop_yield 2.csv there."
        )

    total = sum(1 for _ in open(YIELD_SOURCE, "r", encoding="utf-8")) - 1
    step = max(1, total // YIELD_SAMPLE_ROWS)
    df = pd.read_csv(
        YIELD_SOURCE,
        skiprows=lambda i: i > 0 and (i % step != 0),
    )
    if len(df) > YIELD_SAMPLE_ROWS:
        df = df.sample(YIELD_SAMPLE_ROWS, random_state=RANDOM_STATE)
    df.to_csv(sample_path, index=False)
    return df


def train_yield_prediction() -> dict:
    df = _load_yield_frame()
    target = "Yield_tons_per_hectare"
    cat_cols = ["Region", "Soil_Type", "Crop", "Weather_Condition"]
    bool_cols = ["Fertilizer_Used", "Irrigation_Used"]
    num_cols = ["Rainfall_mm", "Temperature_Celsius", "Days_to_Harvest"]
    feature_cols = cat_cols + bool_cols + num_cols

    X = df[feature_cols].copy()
    for col in bool_cols:
        X[col] = X[col].astype(int)
    y = df[target].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    preprocess = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                cat_cols,
            ),
            ("num", "passthrough", bool_cols + num_cols),
        ]
    )

    models = {
        "xgboost": XGBRegressor(
            n_estimators=250,
            max_depth=6,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestRegressor(
            n_estimators=180, random_state=RANDOM_STATE, n_jobs=-1
        ),
        "linear_regression": LinearRegression(),
        "decision_tree": DecisionTreeRegressor(random_state=RANDOM_STATE, max_depth=12),
    }

    results = {}
    fitted = {}
    for name, estimator in models.items():
        print(f"[yield] training {name}...")
        pipe = Pipeline([("prep", preprocess), ("model", estimator)])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        results[name] = evaluate_regressor(y_test, pred)
        fitted[name] = pipe

    best_name = _best_by(results, "r2")
    if results[best_name]["r2"] < 0:
        print("[yield] WARNING: best R² is negative — check features/target.")

    joblib.dump(
        {
            "model": fitted[best_name],
            "algorithm": best_name,
            "feature_cols": feature_cols,
            "cat_cols": cat_cols,
            "bool_cols": bool_cols,
            "num_cols": num_cols,
            "target": target,
            "task": "yield_prediction",
            "categories": {
                col: sorted(df[col].astype(str).unique().tolist()) for col in cat_cols
            },
        },
        MODELS / "yield_model.pkl",
    )

    comparison = {name: dict(vals) for name, vals in results.items()}
    for metric in ("mae", "rmse", "r2"):
        plot_model_comparison(
            comparison, metric, PLOTS_DIR / f"yield_{metric}_comparison.png"
        )

    slim = {
        "best_algorithm": best_name,
        "n_samples": int(len(df)),
        "feature_cols": feature_cols,
        "target": target,
        "algorithms": comparison,
    }
    print(f"[yield] best={best_name} r2={comparison[best_name]['r2']:.4f}")
    return slim


def main():
    crop_only = "--crop-only" in sys.argv
    crop = train_crop_recommendation()
    payload = {
        "crop_recommendation": crop,
        "fertilizer": {"method": "rule-based", "accuracy": None},
    }
    if crop_only:
        existing_path = RESULTS_DIR / "metrics.json"
        if existing_path.exists():
            import json

            existing = json.loads(existing_path.read_text(encoding="utf-8"))
            if "yield_prediction" in existing:
                payload["yield_prediction"] = existing["yield_prediction"]
    else:
        payload["yield_prediction"] = train_yield_prediction()
    save_metrics(payload, RESULTS_DIR / "metrics.json")
    print(f"Wrote {RESULTS_DIR / 'metrics.json'}")


if __name__ == "__main__":
    main()
