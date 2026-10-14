from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from backend.app.config import ROOT_DIR

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from crop_inference import (  # noqa: E402
    assemble_crop_prediction,
    feature_range_warnings,
    global_importance_factors,
    shap_feature_contributions,
)
from fertilizer_rules import recommend_fertilizer  # noqa: E402

MODELS_DIR = ROOT_DIR / "saved_models"
ML_SAVED = ROOT_DIR / "ml" / "saved_models"
RESULTS_DIR = ROOT_DIR / "results"

_crop = None
_yield = None
_price = None
_vision = {}
_metrics = {}
_shap_crop = None
_shap_yield = None
_tree_importances = None


def _base_tree(model):
    if getattr(model, "estimator_", None) is not None:
        return model.estimator_
    if hasattr(model, "calibrated_classifiers_") and model.calibrated_classifiers_:
        return getattr(model.calibrated_classifiers_[0], "estimator", model)
    return model


def load_artifacts() -> None:
    global _crop, _yield, _price, _metrics, _shap_crop, _shap_yield, _tree_importances, _vision
    crop_path = MODELS_DIR / "crop_model.pkl"
    yield_path = MODELS_DIR / "yield_model.pkl"
    if crop_path.exists():
        _crop = joblib.load(crop_path)
        tree_model = _base_tree(_crop["model"])
        _tree_importances = getattr(tree_model, "feature_importances_", None)
        try:
            import shap

            _shap_crop = shap.TreeExplainer(tree_model)
        except Exception:
            _shap_crop = None
    if yield_path.exists():
        _yield = joblib.load(yield_path)
        try:
            import shap

            inner = _yield["model"]
            estimator = inner.named_steps["model"] if hasattr(inner, "named_steps") else inner
            if hasattr(estimator, "feature_importances_"):
                _shap_yield = shap.TreeExplainer(estimator)
        except Exception:
            _shap_yield = None

    price_path = MODELS_DIR / "price_model.pkl"
    if price_path.exists():
        _price = joblib.load(price_path)

    for task in ("disease",):
        path = MODELS_DIR / f"{task}_model.pkl"
        if path.exists():
            _vision[task] = joblib.load(path)

    metrics_path = RESULTS_DIR / "metrics.json"
    extra_path = ML_SAVED / "metrics.json"
    _metrics = {}
    if metrics_path.exists():
        _metrics.update(json.loads(metrics_path.read_text(encoding="utf-8")))
    if extra_path.exists():
        extra = json.loads(extra_path.read_text(encoding="utf-8"))
        _metrics.update(extra)


def metrics() -> dict:
    return _metrics


def predict_crop(payload: dict) -> dict:
    if _crop is None:
        return _placeholder("crop-recommendation", payload)
    model = _crop["model"]
    cols = _crop["feature_cols"]
    encoder = _crop["label_encoder"]
    X = pd.DataFrame([{c: payload[c] for c in cols}])
    proba = np.asarray(model.predict_proba(X)[0], dtype=float)
    pred_idx = int(np.argmax(proba))
    explanations = []
    if _shap_crop is not None:
        try:
            explanations = shap_feature_contributions(_shap_crop, X, pred_idx)
        except Exception:
            explanations = []
    fallback = []
    if _tree_importances is not None:
        fallback = global_importance_factors(_tree_importances, cols)
    return assemble_crop_prediction(
        classes=encoder.classes_,
        probabilities=proba,
        uncertain_threshold=float(_crop.get("uncertain_threshold", 0.60)),
        algorithm=_crop["algorithm"],
        feature_cols=cols,
        explanations=explanations,
        fallback_factors=fallback,
        input_warnings=feature_range_warnings(payload, _crop.get("feature_ranges", {})),
        probabilities_calibrated=bool(_crop.get("probabilities_calibrated", False)),
    )


def predict_yield(payload: dict) -> dict:
    if _yield is None:
        return _placeholder("yield-prediction", payload)
    model = _yield["model"]
    cols = _yield["feature_cols"]
    X = pd.DataFrame([{c: payload[c] for c in cols}])
    for col in _yield["bool_cols"]:
        X[col] = X[col].astype(int)
    pred = float(model.predict(X)[0])
    shap_rows = []
    if _shap_yield is not None:
        try:
            import shap  # noqa: F401

            transformed = model.named_steps["prep"].transform(X)
            values = _shap_yield.shap_values(transformed)
            arr = np.asarray(values)[0]
            names = list(model.named_steps["prep"].get_feature_names_out())
            for name, raw in sorted(
                zip(names, arr), key=lambda item: abs(float(item[1])), reverse=True
            )[:8]:
                shap_rows.append(
                    {
                        "feature": str(name),
                        "shap_value": round(float(raw), 4),
                        "direction": "supports" if float(raw) >= 0 else "opposes",
                    }
                )
        except Exception:
            shap_rows = []
    return {
        "predicted_yield_t_ha": round(pred, 4),
        "algorithm": _yield["algorithm"],
        "unit": "tons_per_hectare",
        "explanations": shap_rows,
    }


def predict_fertilizer(payload: dict) -> dict:
    result = recommend_fertilizer(
        payload["crop"], payload["N"], payload["P"], payload["K"], payload["ph"]
    )
    result["label"] = "Rule-Based — no ML accuracy applicable"
    result["method"] = "rule-based"
    return result


def predict_price(payload: dict) -> dict:
    if _price is None:
        return _placeholder("market-price", payload)
    model = _price["model"]
    cols = _price["feature_cols"]
    X = pd.DataFrame([{c: payload.get(c) for c in cols}])
    pred = float(model.predict(X)[0])
    return {
        "predicted_price": round(pred, 2),
        "currency": _price.get("currency", "INR/quintal"),
        "algorithm": _price["algorithm"],
        "features_used": cols,
    }


def predict_vision(task: str, image_path: Path) -> dict:
    bundle = _vision.get(task)
    if bundle is None:
        return _placeholder(task, {"image": str(image_path)})
    from backend.app.ml.vision_infer import infer_image

    return infer_image(bundle, image_path, task)


def _placeholder(kind: str, payload: dict) -> dict:
    # TODO: replace with trained-model inference once the matching pickle exists.
    samples = {
        "crop-recommendation": {
            "predicted_crop": "rice",
            "confidence": 0.86,
            "status": "placeholder",
            "note": "Train crop_model.pkl via python train_models.py",
        },
        "disease-detection": {
            "predicted_class": "leaf_blight",
            "confidence": 0.81,
            "gradcam_url": None,
            "note": "Train with python train_publication.py --vision",
        },
        "yield-prediction": {
            "predicted_yield_t_ha": 4.2,
            "algorithm": "placeholder",
        },
        "fertilizer-recommendation": {
            "label": "Rule-Based — no ML accuracy applicable",
            "primary_action": "Apply Urea (placeholder)",
        },
        "market-price": {
            "predicted_price": 2150.0,
            "currency": "INR/quintal",
            "algorithm": "placeholder",
        },
    }
    body = dict(samples.get(kind, {"status": "placeholder"}))
    body["input"] = payload
    body["placeholder"] = True
    return body
