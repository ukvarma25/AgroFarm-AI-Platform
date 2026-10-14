from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import ROOT_DIR, settings
from backend.app.database import Base, engine
from backend.app.ml.artifacts import load_artifacts
from backend.app.models import farm, user  # noqa: F401
from backend.app.routers import (
    auth,
    chatbot,
    dashboard,
    farms,
    metrics,
    predict,
    reports,
    weather,
)

app = FastAPI(
    title="AgroFarm AI",
    version="1.0.0",
    description="Auth, farm records, ML inference, weather, chatbot, and reports.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    try:
        load_artifacts()
    except Exception as exc:
        print(f"[startup] model load warning: {exc}")


app.include_router(auth.router)
app.include_router(farms.router)
app.include_router(predict.router)
app.include_router(metrics.router)
app.include_router(weather.router)
app.include_router(chatbot.router)
app.include_router(reports.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}


uploads = settings.uploads_dir
uploads.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads)), name="uploads")

plots = ROOT_DIR / "plots"
ml_plots = ROOT_DIR / "ml" / "saved_models"
if plots.exists():
    app.mount("/static", StaticFiles(directory=str(plots)), name="static")
elif ml_plots.exists():
    app.mount("/static", StaticFiles(directory=str(ml_plots)), name="static")

