from __future__ import annotations

import json

from sqlalchemy.orm import Session

from backend.app.ml import artifacts
from backend.app.models.farm import Farm, Prediction, SoilData


def store_prediction(
    db: Session,
    farm_id: int | None,
    kind: str,
    payload: dict,
    result: dict,
) -> dict:
    if farm_id is None:
        return result
    row = Prediction(
        farm_id=farm_id,
        prediction_type=kind,
        input_json=json.dumps(payload, default=str),
        result_json=json.dumps(result, default=str),
        confidence=result.get("confidence") or result.get("predicted_yield_t_ha"),
        explanation_json=json.dumps(
            result.get("explanations") or result.get("trace") or {},
            default=str,
        ),
        model_name=str(result.get("algorithm") or result.get("method") or kind),
    )
    db.add(row)
    db.commit()
    result["prediction_id"] = row.id
    result["farm_id"] = farm_id
    return result


def run_tabular_insights(db: Session, farm: Farm, soil: SoilData) -> dict:
    """Populate crop, fertilizer, yield, and market-price cards from the latest soil row."""
    crop_in = {
        "N": soil.nitrogen,
        "P": soil.phosphorus,
        "K": soil.potassium,
        "temperature": soil.temperature or 25,
        "humidity": soil.humidity or 70,
        "ph": soil.ph,
        "rainfall": soil.rainfall or 100,
    }
    crop = artifacts.predict_crop(crop_in)
    store_prediction(db, farm.id, "crop-recommendation", crop_in, crop)
    crop_name = str(crop.get("predicted_crop") or "rice")

    fert_in = {
        "crop": crop_name,
        "N": soil.nitrogen,
        "P": soil.phosphorus,
        "K": soil.potassium,
        "ph": soil.ph,
    }
    fert = artifacts.predict_fertilizer(fert_in)
    store_prediction(db, farm.id, "fertilizer-recommendation", fert_in, fert)

    rainfall_mm = float(soil.rainfall or 0)
    if rainfall_mm < 80:
        rainfall_mm *= 8
    weather = "Rainy" if rainfall_mm >= 800 else "Sunny"
    yield_in = {
        "Region": "South",
        "Soil_Type": farm.soil_type or "Clay",
        "Crop": crop_name.title(),
        "Rainfall_mm": rainfall_mm or 900,
        "Temperature_Celsius": float(soil.temperature or 24),
        "Fertilizer_Used": True,
        "Irrigation_Used": True,
        "Weather_Condition": weather,
        "Days_to_Harvest": 120,
    }
    yield_out = artifacts.predict_yield(yield_in)
    store_prediction(db, farm.id, "yield-prediction", yield_in, yield_out)

    price_in = {
        "crop": crop_name.title(),
        "season": "Kharif",
        "region": "Karnataka",
        "quantity": float(farm.land_size_acres or 10),
    }
    price = artifacts.predict_price(price_in)
    store_prediction(db, farm.id, "market-price", price_in, price)
    return {
        "crop_recommendation": crop,
        "fertilizer_recommendation": fert,
        "yield_prediction": yield_out,
        "market_price": price,
    }
