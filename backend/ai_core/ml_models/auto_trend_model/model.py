import os
import pickle
import uuid
from typing import Dict, Any, Optional
from loguru import logger

MODEL_DIR = "database/ml_models"


class TrendModel:
    """XGBoost/LightGBM ensemble for next-bar direction prediction."""

    def __init__(self):
        self.model = None
        self.feature_names = []
        os.makedirs(MODEL_DIR, exist_ok=True)

    async def train(self, symbol: str, timeframe: str = "1D", lookback_days: int = 365) -> Dict[str, Any]:
        from backend.data_engine.historical_loader import get_historical_loader
        from backend.data_engine.feature_builder import build_features
        import numpy as np

        loader = get_historical_loader()
        df = await loader.get_dataframe(symbol, timeframe, limit=lookback_days)
        if df is None or len(df) < 100:
            return {"error": "Insufficient data"}

        features = build_features(df)
        if features.empty:
            return {"error": "Feature engineering failed"}

        # Target: next bar direction
        future_return = df["close"].shift(-1) / df["close"] - 1
        target = (future_return > 0).astype(int)
        target = target.loc[features.index].dropna()
        features = features.loc[target.index]

        X = features.fillna(0).values
        y = target.values
        self.feature_names = features.columns.tolist()

        # Train/test split
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        try:
            import xgboost as xgb
            self.model = xgb.XGBClassifier(
                n_estimators=100, max_depth=5, learning_rate=0.05,
                use_label_encoder=False, eval_metric="logloss", random_state=42
            )
            self.model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
            accuracy = (self.model.predict(X_test) == y_test).mean()
        except ImportError:
            from sklearn.ensemble import RandomForestClassifier
            self.model = RandomForestClassifier(n_estimators=50, random_state=42)
            self.model.fit(X_train, y_train)
            accuracy = (self.model.predict(X_test) == y_test).mean()

        # Save model
        model_id = str(uuid.uuid4())[:12]
        model_path = f"{MODEL_DIR}/trend_{symbol}_{model_id}.pkl"
        with open(model_path, "wb") as f:
            pickle.dump({"model": self.model, "features": self.feature_names}, f)

        # Save to DB
        await self._save_model_record(model_id, symbol, timeframe, model_path, accuracy)

        logger.info(f"Trend model trained: {symbol} | Accuracy: {accuracy:.2%}")
        return {"model_id": model_id, "accuracy": round(accuracy, 4), "symbol": symbol, "model_path": model_path}

    async def predict(self, symbol: str, timeframe: str = "1D") -> Dict[str, Any]:
        if not self.model:
            return {"direction": "NEUTRAL", "confidence": 0.5}

        from backend.data_engine.historical_loader import get_historical_loader
        from backend.data_engine.feature_builder import build_features

        loader = get_historical_loader()
        df = await loader.get_dataframe(symbol, timeframe, limit=300)
        if df is None or df.empty:
            return {"direction": "NEUTRAL", "confidence": 0.5}

        features = build_features(df)
        if features.empty:
            return {"direction": "NEUTRAL", "confidence": 0.5}

        X = features.fillna(0).values[-1:]
        prob = self.model.predict_proba(X)[0]
        direction = "UP" if prob[1] > 0.5 else "DOWN"
        confidence = max(prob)

        return {"direction": direction, "confidence": round(float(confidence), 4), "symbol": symbol}

    async def _save_model_record(self, model_id: str, symbol: str, timeframe: str, path: str, accuracy: float):
        try:
            from backend.database.connection import get_session
            from backend.database.models.ml_model import MLModel
            async for session in get_session():
                m = MLModel(
                    model_id=model_id,
                    model_type="trend",
                    name=f"Trend Model {symbol}",
                    version="1.0",
                    symbol=symbol,
                    timeframe=timeframe,
                    file_path=path,
                    accuracy=accuracy,
                    is_active=1,
                    feature_names=self.feature_names,
                )
                session.add(m)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to save model record: {e}")
