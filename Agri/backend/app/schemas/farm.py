from datetime import datetime

from pydantic import BaseModel, Field


class FarmCreate(BaseModel):
    name: str
    address: str
    land_size_acres: float = Field(..., gt=0)
    soil_type: str = "Other"
    lat: float | None = None
    lng: float | None = None


class SoilCreate(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    moisture: float = 0
    temperature: float = 25
    humidity: float = 70
    rainfall: float = 100


class FarmOut(BaseModel):
    id: int
    user_id: int
    name: str
    address: str
    lat: float | None
    lng: float | None
    land_size_acres: float
    soil_type: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class SoilOut(BaseModel):
    id: int
    farm_id: int
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    moisture: float
    temperature: float
    humidity: float
    rainfall: float
    recorded_at: datetime | None = None

    model_config = {"from_attributes": True}
