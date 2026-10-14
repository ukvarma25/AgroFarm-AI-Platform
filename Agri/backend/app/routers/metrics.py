from fastapi import APIRouter

from backend.app.ml.artifacts import metrics

router = APIRouter(tags=["models"])


@router.get("/models/metrics")
def get_metrics():
    return metrics()
