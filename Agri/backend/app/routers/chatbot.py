from __future__ import annotations

import json

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.core.deps import get_current_user
from backend.app.database import get_db
from backend.app.models.farm import Farm, Prediction, SoilData
from backend.app.models.user import User

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class AskIn(BaseModel):
    message: str
    history: list[dict] = Field(default_factory=list)


def _farm_context(user: User, db: Session) -> str:
    farm = db.query(Farm).filter(Farm.user_id == user.id).first()
    if farm is None:
        return "The farmer has not created a farm yet."
    soil = (
        db.query(SoilData)
        .filter(SoilData.farm_id == farm.id)
        .order_by(SoilData.id.desc())
        .first()
    )
    preds = (
        db.query(Prediction)
        .filter(Prediction.farm_id == farm.id)
        .order_by(Prediction.id.desc())
        .limit(6)
        .all()
    )
    soil_txt = "No soil records yet."
    if soil:
        soil_txt = (
            f"N={soil.nitrogen}, P={soil.phosphorus}, K={soil.potassium}, "
            f"pH={soil.ph}, temp={soil.temperature}"
        )
    pred_txt = []
    for row in preds:
        try:
            body = json.loads(row.result_json)
        except Exception:
            body = {}
        pred_txt.append(f"{row.prediction_type}: {body}")
    return (
        f"Farmer: {user.full_name} ({user.role}). "
        f"Farm: {farm.name}, {farm.address}, {farm.land_size_acres} acres, soil {farm.soil_type}. "
        f"Latest soil: {soil_txt}. Recent predictions: {pred_txt or 'none'}."
    )


@router.post("/ask")
def ask(payload: AskIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    context = _farm_context(user, db)
    system = (
        "You are AgroFarm AI, a precision-agriculture assistant. "
        "Answer using the farmer's real farm/soil/prediction context. "
        "If data is missing, say so. Do not invent lab results. "
        f"Context: {context}"
    )
    if settings.groq_api_key:
        messages = [{"role": "system", "content": system}]
        prior = payload.history[-8:]
        if (
            prior
            and prior[-1].get("role") == "user"
            and prior[-1].get("content") == payload.message
        ):
            prior = prior[:-1]
        for item in prior:
            role = item.get("role", "user")
            if role not in ("user", "assistant", "system"):
                role = "user"
            messages.append({"role": role, "content": item.get("content", "")})
        messages.append({"role": "user", "content": payload.message})
        try:
            with httpx.Client(timeout=30) as client:
                res = client.post(
                    f"{settings.groq_base_url.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {settings.groq_api_key}"},
                    json={
                        "model": settings.groq_model,
                        "messages": messages,
                        "temperature": 0.3,
                    },
                )
                res.raise_for_status()
                answer = res.json()["choices"][0]["message"]["content"]
            return {
                "answer": answer,
                "provider": "groq",
                "model": settings.groq_model,
                "context_used": True,
            }
        except Exception:
            return {
                "answer": (
                    "Groq is unavailable right now, so I could not generate an AI answer. "
                    "Please check GROQ_API_KEY and GROQ_MODEL in backend/.env, then restart the backend."
                ),
                "provider": "fallback",
                "context_used": True,
            }
    answer = (
        "Groq API key is not set, so this is a grounded local reply. "
        f"{context} You asked: {payload.message}. "
        "Add GROQ_API_KEY in backend/.env for Groq chat responses."
    )
    return {"answer": answer, "provider": "local", "context_used": True}
