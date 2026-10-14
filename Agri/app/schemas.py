from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CropFeatures(BaseModel):
    N: float = Field(..., description="Nitrogen content in soil")
    P: float = Field(..., description="Phosphorus content in soil")
    K: float = Field(..., description="Potassium content in soil")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Relative humidity %")
    ph: float = Field(..., description="Soil pH")
    rainfall: float = Field(..., description="Rainfall in mm")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "N": 90,
                    "P": 42,
                    "K": 43,
                    "temperature": 20.9,
                    "humidity": 82.0,
                    "ph": 6.5,
                    "rainfall": 202.9,
                }
            ]
        }
    }

    @field_validator("N")
    @classmethod
    def n_must_be_physical(cls, value: float) -> float:
        if value < 0:
            raise ValueError("N cannot be negative")
        if value > 400:
            raise ValueError("N is outside a plausible soil-test range (0-400)")
        return value

    @field_validator("P")
    @classmethod
    def p_must_be_physical(cls, value: float) -> float:
        if value < 0:
            raise ValueError("P cannot be negative")
        if value > 400:
            raise ValueError("P is outside a plausible soil-test range (0-400)")
        return value

    @field_validator("K")
    @classmethod
    def k_must_be_physical(cls, value: float) -> float:
        if value < 0:
            raise ValueError("K cannot be negative")
        if value > 400:
            raise ValueError("K is outside a plausible soil-test range (0-400)")
        return value

    @field_validator("humidity")
    @classmethod
    def humidity_range(cls, value: float) -> float:
        if not 0 <= value <= 100:
            raise ValueError("Humidity must be between 0 and 100")
        return value

    @field_validator("ph")
    @classmethod
    def ph_range(cls, value: float) -> float:
        if not 0 <= value <= 14:
            raise ValueError("pH must be between 0 and 14")
        return value

    @field_validator("rainfall")
    @classmethod
    def rainfall_range(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Rainfall cannot be negative")
        if value > 5000:
            raise ValueError("Rainfall is outside a plausible range (0-5000 mm)")
        return value

    @field_validator("temperature")
    @classmethod
    def temperature_domain(cls, value: float) -> float:
        if not 0 <= value <= 50:
            raise ValueError(
                "Temperature must be between 0 and 50 C for this crop model"
            )
        return value


class CropAlternative(BaseModel):
    crop: str
    probability: float


class ShapContribution(BaseModel):
    feature: str
    shap_value: float
    direction: str
    bar: int


class CropPredictResponse(BaseModel):
    predicted_crop: str
    confidence: float
    confidence_level: Literal["high", "moderate", "low", "uncertain"]
    status: Literal["certain", "uncertain"]
    recommendation: str
    alternatives: list[CropAlternative]
    top_k: list[CropAlternative]
    important_factors: list[str]
    explanations: list[ShapContribution]
    algorithm: str
    probabilities_calibrated: bool
    uncertain_threshold: float
    features_used: list[str]
    input_warnings: list[str]
    disclaimer: str


class YieldFeatures(BaseModel):
    Region: Literal["North", "South", "East", "West"]
    Soil_Type: Literal["Sandy", "Clay", "Loam", "Silt", "Peaty", "Chalky"]
    Crop: str = Field(..., examples=["Rice", "Wheat", "Cotton", "Soybean", "Barley"])
    Rainfall_mm: float
    Temperature_Celsius: float
    Fertilizer_Used: bool
    Irrigation_Used: bool
    Weather_Condition: Literal["Sunny", "Rainy", "Cloudy"]
    Days_to_Harvest: int = Field(..., ge=1, le=365)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "Region": "South",
                    "Soil_Type": "Clay",
                    "Crop": "Rice",
                    "Rainfall_mm": 992.67,
                    "Temperature_Celsius": 18.03,
                    "Fertilizer_Used": True,
                    "Irrigation_Used": True,
                    "Weather_Condition": "Rainy",
                    "Days_to_Harvest": 140,
                }
            ]
        }
    }


class YieldPredictResponse(BaseModel):
    predicted_yield_t_ha: float
    algorithm: str
    unit: str = "tons_per_hectare"


class FertilizerRequest(BaseModel):
    crop: str = Field(..., examples=["rice"])
    N: float
    P: float
    K: float
    ph: float = Field(..., ge=0, le=14)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"crop": "rice", "N": 20, "P": 50, "K": 50, "ph": 4.8}
            ]
        }
    }


class LabeledCropRow(CropFeatures):
    label: str = Field(..., description="True crop name for evaluation")


class CropEvaluateRequest(BaseModel):
    rows: list[LabeledCropRow]


class LabeledYieldRow(YieldFeatures):
    Yield_tons_per_hectare: float


class YieldEvaluateRequest(BaseModel):
    rows: list[LabeledYieldRow]
