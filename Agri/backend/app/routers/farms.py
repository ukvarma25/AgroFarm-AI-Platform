from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.core.deps import get_current_user
from backend.app.database import get_db
from backend.app.models.farm import Farm, SoilData
from backend.app.models.user import User
from backend.app.schemas.farm import FarmCreate, FarmOut, SoilCreate, SoilOut
from backend.app.utils.insights import run_tabular_insights
from backend.app.utils.uploads import save_farm_image

router = APIRouter(prefix="/farm", tags=["farm"])


def _owned_farm(farm_id: int, user: User, db: Session) -> Farm:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    if farm.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not your farm")
    return farm


@router.post("/create", response_model=FarmOut)
def create_farm(
    payload: FarmCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farm = Farm(
        user_id=user.id,
        name=payload.name,
        address=payload.address,
        land_size_acres=payload.land_size_acres,
        soil_type=payload.soil_type,
        lat=payload.lat,
        lng=payload.lng,
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.get("/mine")
def my_farms(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farms = db.query(Farm).filter(Farm.user_id == user.id).all()
    return [FarmOut.model_validate(f).model_dump() for f in farms]


@router.get("/{farm_id}", response_model=FarmOut)
def get_farm(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _owned_farm(farm_id, user, db)


@router.post("/{farm_id}/soil-data", response_model=SoilOut)
def add_soil(
    farm_id: int,
    payload: SoilCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farm = _owned_farm(farm_id, user, db)
    row = SoilData(
        farm_id=farm.id,
        nitrogen=payload.nitrogen,
        phosphorus=payload.phosphorus,
        potassium=payload.potassium,
        ph=payload.ph,
        moisture=payload.moisture,
        temperature=payload.temperature,
        humidity=payload.humidity,
        rainfall=payload.rainfall,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    try:
        run_tabular_insights(db, farm, row)
    except Exception as exc:
        print(f"[soil] insight refresh skipped: {exc}")
    return row


@router.get("/{farm_id}/soil-data")
def list_soil(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farm = _owned_farm(farm_id, user, db)
    rows = (
        db.query(SoilData)
        .filter(SoilData.farm_id == farm.id)
        .order_by(SoilData.id.desc())
        .all()
    )
    return [SoilOut.model_validate(r).model_dump() for r in rows]


@router.post("/{farm_id}/upload-image")
def upload_image(
    farm_id: int,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farm = _owned_farm(farm_id, user, db)
    dest = save_farm_image(farm.id, file)
    return {
        "farm_id": farm.id,
        "path": str(dest.as_posix()),
        "filename": dest.name,
        "url": f"/uploads/{farm.id}/{dest.name}",
    }
