from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from crop_inference import (
    assemble_crop_prediction,
    feature_range_warnings,
    global_importance_factors,
    shap_feature_contributions,
)
from evaluation import evaluate_classifier, evaluate_regressor
from fertilizer_rules import recommend_fertilizer
from app.schemas import (
    CropEvaluateRequest,
    CropFeatures,
    CropPredictResponse,
    FertilizerRequest,
    YieldEvaluateRequest,
    YieldFeatures,
    YieldPredictResponse,
)

ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / "saved_models"
RESULTS_DIR = ROOT / "results"
PLOTS_DIR = ROOT / "plots"
FRONTEND_DIR = ROOT / "frontend"

app = FastAPI(
    title="AgroFarm AI — Crop Recommendation API",
    description=(
        "Machine-learning crop recommendation from soil N/P/K, pH, temperature, "
        "humidity, and rainfall. Responses include calibrated top-3 probabilities, "
        "an uncertainty flag, and SHAP feature contributions. This is not a "
        "guarantee of what should be grown."
    ),
    version="0.2.0",
)

_crop_bundle = None
_yield_bundle = None
_metrics = None
_shap_explainer = None
_tree_importances = None


def _base_tree_estimator(model):
    if getattr(model, "estimator_", None) is not None:
        return model.estimator_
    if hasattr(model, "calibrated_classifiers_") and model.calibrated_classifiers_:
        return getattr(model.calibrated_classifiers_[0], "estimator", model)
    return model


def _load_artifacts():
    global _crop_bundle, _yield_bundle, _metrics, _shap_explainer, _tree_importances
    crop_path = MODELS_DIR / "crop_model.pkl"
    yield_path = MODELS_DIR / "yield_model.pkl"
    metrics_path = RESULTS_DIR / "metrics.json"
    if not crop_path.exists() or not yield_path.exists():
        raise RuntimeError(
            "Trained models not found. Run `python train_models.py` first."
        )
    _crop_bundle = joblib.load(crop_path)
    _yield_bundle = joblib.load(yield_path)
    _metrics = (
        json.loads(metrics_path.read_text(encoding="utf-8"))
        if metrics_path.exists()
        else {}
    )
    tree_model = _base_tree_estimator(_crop_bundle["model"])
    _tree_importances = getattr(tree_model, "feature_importances_", None)
    try:
        import shap

        _shap_explainer = shap.TreeExplainer(tree_model)
    except Exception:
        _shap_explainer = None


@app.on_event("startup")
def startup():
    _load_artifacts()


@app.get("/", include_in_schema=False)
def ui():
    index = FRONTEND_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Frontend not found.")
    return FileResponse(index)


@app.get("/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "crop_model": bool(_crop_bundle),
        "yield_model": bool(_yield_bundle),
        "crop_algorithm": _crop_bundle["algorithm"] if _crop_bundle else None,
        "yield_algorithm": _yield_bundle["algorithm"] if _yield_bundle else None,
        "probabilities_calibrated": bool(
            _crop_bundle.get("probabilities_calibrated") if _crop_bundle else False
        ),
        "uncertain_threshold": (
            _crop_bundle.get("uncertain_threshold") if _crop_bundle else None
        ),
        "shap_available": _shap_explainer is not None,
    }


@app.get("/metrics", tags=["performance"])
def get_all_metrics():
    return _metrics


@app.get("/metrics/{task}", tags=["performance"])
def get_task_metrics(task: str):
    if task not in _metrics:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown task '{task}'. Try: {list(_metrics.keys())}",
        )
    return _metrics[task]


@app.get("/plots", tags=["performance"])
def list_plots():
    files = sorted(p.name for p in PLOTS_DIR.glob("*.png"))
    return {"plots": files, "hint": "Open /static/{filename} to view a chart."}


@app.post("/predict/crop", response_model=CropPredictResponse, tags=["predict"])
def predict_crop(payload: CropFeatures):
    model = _crop_bundle["model"]
    cols = _crop_bundle["feature_cols"]
    encoder = _crop_bundle["label_encoder"]
    X = pd.DataFrame([{c: getattr(payload, c) for c in cols}])
    proba = np.asarray(model.predict_proba(X)[0], dtype=float)
    pred_idx = int(np.argmax(proba))

    explanations = []
    if _shap_explainer is not None:
        try:
            explanations = shap_feature_contributions(_shap_explainer, X, pred_idx)
        except Exception:
            explanations = []

    fallback = []
    if _tree_importances is not None:
        fallback = global_importance_factors(_tree_importances, cols)

    body = assemble_crop_prediction(
        classes=encoder.classes_,
        probabilities=proba,
        uncertain_threshold=float(_crop_bundle.get("uncertain_threshold", 0.60)),
        algorithm=_crop_bundle["algorithm"],
        feature_cols=cols,
        explanations=explanations,
        fallback_factors=fallback,
        input_warnings=feature_range_warnings(
            payload.model_dump(), _crop_bundle.get("feature_ranges", {})
        ),
        probabilities_calibrated=bool(
            _crop_bundle.get("probabilities_calibrated", False)
        ),
    )
    return CropPredictResponse(**body)


@app.post("/predict/yield", response_model=YieldPredictResponse, tags=["predict"])
def predict_yield(payload: YieldFeatures):
    model = _yield_bundle["model"]
    cols = _yield_bundle["feature_cols"]
    row = payload.model_dump()
    X = pd.DataFrame([{c: row[c] for c in cols}])
    for col in _yield_bundle["bool_cols"]:
        X[col] = X[col].astype(int)
    pred = float(model.predict(X)[0])
    return YieldPredictResponse(
        predicted_yield_t_ha=round(pred, 4),
        algorithm=_yield_bundle["algorithm"],
    )


@app.post("/predict/fertilizer", tags=["predict"])
def predict_fertilizer(payload: FertilizerRequest):
    return recommend_fertilizer(
        payload.crop, payload.N, payload.P, payload.K, payload.ph
    )


@app.post("/evaluate/crop", tags=["performance"])
def evaluate_crop_batch(payload: CropEvaluateRequest):
    if len(payload.rows) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 labeled rows.")
    model = _crop_bundle["model"]
    cols = _crop_bundle["feature_cols"]
    X = pd.DataFrame([{c: getattr(row, c) for c in cols} for row in payload.rows])
    y_true = [row.label for row in payload.rows]
    y_pred = _crop_bundle["label_encoder"].inverse_transform(model.predict(X))
    y_proba = model.predict_proba(X)
    metrics = evaluate_classifier(y_true, y_pred, y_proba, labels=_crop_bundle["labels"])
    metrics.pop("confusion_matrix", None)
    metrics.pop("classification_report", None)
    return {
        "n": len(payload.rows),
        "metrics": metrics,
        "algorithm": _crop_bundle["algorithm"],
    }


@app.post("/evaluate/yield", tags=["performance"])
def evaluate_yield_batch(payload: YieldEvaluateRequest):
    if len(payload.rows) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 labeled rows.")
    model = _yield_bundle["model"]
    cols = _yield_bundle["feature_cols"]
    X = pd.DataFrame([{c: row.model_dump()[c] for c in cols} for row in payload.rows])
    for col in _yield_bundle["bool_cols"]:
        X[col] = X[col].astype(int)
    y_true = [row.Yield_tons_per_hectare for row in payload.rows]
    y_pred = model.predict(X)
    return {
        "n": len(payload.rows),
        "metrics": evaluate_regressor(y_true, y_pred),
        "algorithm": _yield_bundle["algorithm"],
    }


if PLOTS_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(PLOTS_DIR)), name="static")
