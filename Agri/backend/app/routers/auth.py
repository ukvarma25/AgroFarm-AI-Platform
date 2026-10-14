from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.deps import get_current_user
from backend.app.core.security import create_access_token, hash_password, verify_password
from backend.app.database import get_db
from backend.app.models.farm import Farm
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_payload(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
    }


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        full_name=payload.full_name,
        email=str(payload.email).lower(),
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.flush()
    farm = Farm(
        user_id=user.id,
        name=payload.farm_name,
        address=payload.farm_location,
        land_size_acres=payload.land_size_acres,
        soil_type=payload.soil_type,
        lat=payload.lat,
        lng=payload.lng,
    )
    db.add(farm)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.email, {"role": user.role, "name": user.full_name})
    return TokenResponse(access_token=token, user=_user_payload(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == str(payload.email).lower()).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(user.email, {"role": user.role, "name": user.full_name})
    return TokenResponse(access_token=token, user=_user_payload(user))


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return _user_payload(user)
