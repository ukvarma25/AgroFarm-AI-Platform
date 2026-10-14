from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.core.deps import get_current_user
from backend.app.database import get_db
from backend.app.models.farm import Farm
from backend.app.models.user import User

router = APIRouter(tags=["weather"])


def _alerts(temp: float, wind: float, rain: float) -> list[dict]:
    alerts = []
    if rain >= 15:
        alerts.append({"type": "heavy_rain", "message": "Heavy rain risk — protect harvested produce."})
    if temp <= 4:
        alerts.append({"type": "frost_risk", "message": "Frost risk — cover sensitive crops overnight."})
    if temp >= 38:
        alerts.append({"type": "heatwave", "message": "Heatwave — irrigate in early morning/evening."})
    if wind >= 10:
        alerts.append({"type": "high_wind", "message": "High wind — secure shade nets and young plants."})
    if not alerts:
        alerts.append({"type": "normal", "message": "No severe weather alerts for this location."})
    return alerts


def fetch_weather_for_farm(farm: Farm) -> dict:
    lat = farm.lat if farm.lat is not None else 12.9716
    lng = farm.lng if farm.lng is not None else 77.5946
    source = "open-meteo"
    temp = wind = rain = 0.0
    description = "unknown"
    if settings.openweather_api_key:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lng,
            "appid": settings.openweather_api_key,
            "units": "metric",
        }
        try:
            with httpx.Client(timeout=12) as client:
                res = client.get(url, params=params)
                res.raise_for_status()
                data = res.json()
            temp = float(data["main"]["temp"])
            wind = float(data.get("wind", {}).get("speed", 0))
            rain = float(data.get("rain", {}).get("1h", 0) or data.get("rain", {}).get("3h", 0) or 0)
            description = data.get("weather", [{}])[0].get("description", "")
            source = "openweathermap"
        except Exception:
            source = "open-meteo-fallback"
    if source != "openweathermap":
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lng,
            "current": "temperature_2m,wind_speed_10m,precipitation",
        }
        try:
            with httpx.Client(timeout=12) as client:
                res = client.get(url, params=params)
                res.raise_for_status()
                data = res.json()["current"]
            temp = float(data.get("temperature_2m", 0))
            wind = float(data.get("wind_speed_10m", 0)) / 3.6
            rain = float(data.get("precipitation", 0))
            description = "current conditions"
            source = "open-meteo"
        except Exception:
            return {
                "farm_id": farm.id,
                "lat": lat,
                "lng": lng,
                "temperature_c": 0,
                "wind_ms": 0,
                "precipitation_mm": 0,
                "description": "Weather provider unavailable — add OPENWEATHER_API_KEY or retry.",
                "source": "offline",
                "alerts": [
                    {
                        "type": "provider_down",
                        "message": "Live weather could not be fetched. Set OPENWEATHER_API_KEY in backend/.env.",
                    }
                ],
            }
    return {
        "farm_id": farm.id,
        "lat": lat,
        "lng": lng,
        "temperature_c": temp,
        "wind_ms": round(wind, 2),
        "precipitation_mm": rain,
        "description": description,
        "source": source,
        "alerts": _alerts(temp, wind, rain),
    }


@router.get("/weather-alert")
def weather_alert(
    farm_id: int | None = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farm = None
    if farm_id:
        farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == user.id).first()
    else:
        farm = db.query(Farm).filter(Farm.user_id == user.id).first()
    if farm is None:
        raise HTTPException(status_code=404, detail="Create a farm first")
    return fetch_weather_for_farm(farm)
