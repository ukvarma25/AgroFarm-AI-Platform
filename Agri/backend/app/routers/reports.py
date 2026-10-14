from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.deps import get_current_user
from backend.app.database import get_db
from backend.app.models.farm import Farm, Prediction, SoilData
from backend.app.models.user import User
from backend.app.routers.weather import fetch_weather_for_farm

router = APIRouter(tags=["reports"])


@router.get("/ai-report")
def ai_report(
    farm_id: int | None = Query(None),
    format: str = Query("json"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farm = (
        db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == user.id).first()
        if farm_id
        else db.query(Farm).filter(Farm.user_id == user.id).first()
    )
    if farm is None:
        return {"detail": "No farm yet"}
    soil = (
        db.query(SoilData)
        .filter(SoilData.farm_id == farm.id)
        .order_by(SoilData.id.desc())
        .first()
    )
    latest = {}
    for row in (
        db.query(Prediction)
        .filter(Prediction.farm_id == farm.id)
        .order_by(Prediction.id.desc())
        .all()
    ):
        if row.prediction_type not in latest:
            try:
                latest[row.prediction_type] = json.loads(row.result_json)
            except Exception:
                latest[row.prediction_type] = row.result_json
    try:
        weather = fetch_weather_for_farm(farm)
    except Exception as exc:
        weather = {"error": str(exc)}
    body = {
        "farmer": {"name": user.full_name, "email": user.email, "role": user.role},
        "farm": {
            "id": farm.id,
            "name": farm.name,
            "location": farm.address,
            "lat": farm.lat,
            "lng": farm.lng,
            "land_size_acres": farm.land_size_acres,
            "soil_type": farm.soil_type,
        },
        "latest_soil": (
            {
                "N": soil.nitrogen,
                "P": soil.phosphorus,
                "K": soil.potassium,
                "ph": soil.ph,
                "temperature": soil.temperature,
            }
            if soil
            else None
        ),
        "crop_recommendation": latest.get("crop-recommendation"),
        "disease_result": latest.get("disease-detection"),
        "yield_prediction": latest.get("yield-prediction"),
        "fertilizer_recommendation": latest.get("fertilizer-recommendation"),
        "market_price": latest.get("market-price"),
        "weather_alert": weather,
        "shap_or_gradcam_refs": {
            "crop": (latest.get("crop-recommendation") or {}).get("explanations"),
            "yield": (latest.get("yield-prediction") or {}).get("explanations"),
            "disease_gradcam": (latest.get("disease-detection") or {}).get("gradcam_url"),
        },
    }
    markdown = _to_markdown(body)
    body["markdown"] = markdown
    if format == "markdown":
        return {"markdown": markdown}
    return body


def _to_markdown(body: dict) -> str:
    farm = body["farm"]
    soil = body["latest_soil"]
    crop = body.get("crop_recommendation") or {}
    lines = [
        f"# AgroFarm AI report — {farm['name']}",
        f"Farmer: {body['farmer']['name']} ({body['farmer']['role']})",
        f"Location: {farm['location']} | {farm['land_size_acres']} acres | soil {farm['soil_type']}",
        "",
        "## Soil",
        json.dumps(soil, indent=2) if soil else "No soil data",
        "",
        "## Crop recommendation",
        f"{crop.get('predicted_crop', 'n/a')} (confidence {crop.get('confidence', 'n/a')})",
        crop.get("recommendation", ""),
        "",
        "## Yield",
        json.dumps(body.get("yield_prediction"), indent=2),
        "",
        "## Fertilizer",
        json.dumps(body.get("fertilizer_recommendation"), indent=2),
        "",
        "## Disease detection",
        json.dumps(body.get("disease_result"), indent=2),
        "",
        "## Weather",
        json.dumps(body.get("weather_alert"), indent=2),
        "",
        "## Explainability refs",
        json.dumps(body.get("shap_or_gradcam_refs"), indent=2),
    ]
    return "\n".join(lines)
