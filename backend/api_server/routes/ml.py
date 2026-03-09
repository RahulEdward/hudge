from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/ml", tags=["ML Lab"])


class TrainRequest(BaseModel):
    model_type: str  # trend / regime / volatility
    symbol: str
    timeframe: str = "1D"
    lookback_days: int = 365


class PredictRequest(BaseModel):
    model_id: str
    symbol: str
    timeframe: str = "1D"


@router.post("/train")
async def train_model(req: TrainRequest):
    from backend.ai_core.ml_models.auto_trend_model.model import TrendModel
    from backend.ai_core.ml_models.regime_detection.model import RegimeModel
    if req.model_type == "trend":
        model = TrendModel()
        result = await model.train(req.symbol, req.timeframe, req.lookback_days)
    elif req.model_type == "regime":
        model = RegimeModel()
        result = await model.train(req.symbol, req.timeframe, req.lookback_days)
    else:
        result = {"error": f"Unknown model type: {req.model_type}"}
    return {"success": True, "result": result}


@router.get("/models")
async def list_models():
    from backend.database.connection import get_session
    from backend.database.models.ml_model import MLModel
    from sqlalchemy import select
    async for session in get_session():
        result = await session.execute(select(MLModel))
        models = result.scalars().all()
        return {"success": True, "models": [m.__dict__ for m in models]}


@router.post("/predict")
async def predict(req: PredictRequest):
    from backend.ai_core.ml_models.auto_trend_model.model import TrendModel
    model = TrendModel()
    prediction = await model.predict(req.symbol, req.timeframe)
    return {"success": True, "prediction": prediction}
