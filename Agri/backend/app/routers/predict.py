from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.deps import get_current_user
from backend.app.database import get_db
from backend.app.ml import artifacts
from backend.app.models.farm import Farm
from backend.app.models.user import User
from backend.app.utils.insights import store_prediction
from backend.app.utils.uploads import save_farm_image

router = APIRouter(tags=["predict"])


class CropIn(BaseModel):
    farm_id: int | None = None
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float


class YieldIn(BaseModel):
    farm_id: int | None = None
    Region: str = "South"
    Soil_Type: str = "Clay"
    Crop: str = "Rice"
    Rainfall_mm: float = 900
    Temperature_Celsius: float = 24
    Fertilizer_Used: bool = True
    Irrigation_Used: bool = True
    Weather_Condition: str = "Rainy"
    Days_to_Harvest: int = Field(120, ge=1, le=365)


class FertilizerIn(BaseModel):
    farm_id: int | None = None
    crop: str
    N: float
    P: float
    K: float
    ph: float


class PriceIn(BaseModel):
    farm_id: int | None = None
    crop: str
    season: str = "Kharif"
    region: str = "Karnataka"
    quantity: float = 10


def _store(
    db: Session,
    farm_id: int | None,
    user: User,
    kind: str,
    payload: dict,
    result: dict,
):
    if farm_id is None:
        farm = db.query(Farm).filter(Farm.user_id == user.id).first()
        farm_id = farm.id if farm else None
    return store_prediction(db, farm_id, kind, payload, result)


@router.post("/predict/crop-recommendation")
@router.post("/predict/crop")
def crop(payload: CropIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = payload.model_dump()
    result = artifacts.predict_crop(data)
    return _store(db, payload.farm_id, user, "crop-recommendation", data, result)


@router.post("/predict/yield-prediction")
@router.post("/predict/yield")
def yield_pred(payload: YieldIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = payload.model_dump()
    result = artifacts.predict_yield(data)
    return _store(db, payload.farm_id, user, "yield-prediction", data, result)


@router.post("/predict/fertilizer-recommendation")
@router.post("/predict/fertilizer")
def fertilizer(payload: FertilizerIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = payload.model_dump()
    result = artifacts.predict_fertilizer(data)
    return _store(db, payload.farm_id, user, "fertilizer-recommendation", data, result)


@router.post("/predict/market-price")
def market_price(payload: PriceIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = payload.model_dump()
    result = artifacts.predict_price(data)
    return _store(db, payload.farm_id, user, "market-price", data, result)


def _vision_endpoint(task: str, farm_id: int, file: UploadFile, user: User, db: Session):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == user.id).first()
    if farm is None and user.role != "admin":
        raise HTTPException(status_code=404, detail="Farm not found")
    dest = save_farm_image(farm_id, file)
    result = artifacts.predict_vision(task, Path(dest))
    result["image_url"] = f"/uploads/{farm_id}/{dest.name}"
    if result.get("gradcam_url"):
        cam_name = Path(result["gradcam_url"]).name
        result["gradcam_url"] = f"/uploads/{farm_id}/{cam_name}"
    return _store(db, farm_id, user, f"{task}-detection", {"image": dest.name}, result)


@router.post("/predict/disease-detection")
def disease(
    farm_id: int = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _vision_endpoint("disease", farm_id, file, user, db)


