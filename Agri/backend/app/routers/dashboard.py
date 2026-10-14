from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.deps import get_current_user
from backend.app.database import get_db
from backend.app.ml.artifacts import metrics
from backend.app.models.farm import Farm, Prediction, SoilData
from backend.app.models.user import User
from backend.app.routers.weather import fetch_weather_for_farm

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/summary")
def summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farms = db.query(Farm).filter(Farm.user_id == user.id).all()
    farm_ids = [f.id for f in farms]
    soils = (
        db.query(SoilData)
        .filter(SoilData.farm_id.in_(farm_ids))
        .order_by(SoilData.id.desc())
        .all()
        if farm_ids
        else []
    )
    preds = (
        db.query(Prediction)
        .filter(Prediction.farm_id.in_(farm_ids))
        .order_by(Prediction.id.desc())
        .all()
        if farm_ids
        else []
    )
    latest_by_type = {}
    for row in preds:
        if row.prediction_type not in latest_by_type:
            try:
                latest_by_type[row.prediction_type] = json.loads(row.result_json)
            except Exception:
                latest_by_type[row.prediction_type] = {}
            latest_by_type[row.prediction_type]["created_at"] = str(row.created_at)
    soil_health = 72
    if soils:
        ph = soils[0].ph
        soil_health = int(max(40, min(96, 100 - abs(ph - 6.5) * 12)))
    m = metrics()
    crop_m = m.get("crop_recommendation", {})
    crops = set()
    yield_history = []
    for row in preds:
        try:
            body = json.loads(row.result_json)
        except Exception:
            body = {}
        if row.prediction_type == "crop-recommendation" and body.get("predicted_crop"):
            crops.add(body["predicted_crop"])
        if row.prediction_type == "yield-prediction" and body.get("predicted_yield_t_ha") is not None:
            yield_history.append(
                {
                    "at": str(row.created_at)[5:16],
                    "yield": body["predicted_yield_t_ha"],
                }
            )
    yield_history = list(reversed(yield_history[:8]))
    weather = None
    weather_alerts = []
    if farms:
        try:
            weather = fetch_weather_for_farm(farms[0])
            weather_alerts = [
                {"title": a.get("type", "alert"), "detail": a.get("message", ""), "at": "now"}
                for a in weather.get("alerts", [])
            ]
        except Exception as exc:
            weather_alerts = [{"title": "weather", "detail": str(exc), "at": "now"}]
    alerts = weather_alerts or [
        {"title": p.prediction_type, "detail": p.model_name, "at": str(p.created_at)}
        for p in preds[:3]
    ]
    return {
        "user": {"full_name": user.full_name, "role": user.role, "email": user.email},
        "stats": {
            "total_fields": len(farms),
            "total_area": round(sum(f.land_size_acres for f in farms), 2),
            "crops_grown": len(crops) or (1 if latest_by_type.get("crop-recommendation") else 0),
            "soil_health": soil_health,
        },
        "farms": [
            {
                "id": f.id,
                "name": f.name,
                "address": f.address,
                "land_size_acres": f.land_size_acres,
                "soil_type": f.soil_type,
                "lat": f.lat,
                "lng": f.lng,
            }
            for f in farms
        ],
        "latest_soil": (
            {
                "N": soils[0].nitrogen,
                "P": soils[0].phosphorus,
                "K": soils[0].potassium,
                "ph": soils[0].ph,
                "temperature": soils[0].temperature,
                "humidity": soils[0].humidity,
                "rainfall": soils[0].rainfall,
            }
            if soils
            else None
        ),
        "latest": latest_by_type,
        "weather": weather,
        "alerts": alerts[:3],
        "reports": [
            {"title": p.prediction_type.replace("-", " ").title(), "at": str(p.created_at)}
            for p in preds[:3]
        ],
        "health": {
            "overall": soil_health,
            "soil": soil_health,
            "crop": int((latest_by_type.get("crop-recommendation") or {}).get("confidence", 0.7) * 100),
            "disease": 100 - int((latest_by_type.get("disease-detection") or {}).get("confidence", 0.2) * 40),
            "nutrient": soil_health,
        },
        "yield_history": yield_history,
        "model_hint": {
            "crop_best": crop_m.get("best_algorithm"),
            "n_samples": crop_m.get("n_samples"),
        },
    }
