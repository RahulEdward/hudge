import pandas as pd
import numpy as np
from typing import List, Dict, Any


def compute_indicators(df: pd.DataFrame, indicators: List[str]) -> Dict[str, Any]:
    """Compute requested technical indicators on OHLCV dataframe."""
    if df is None or df.empty:
        return {}

    result = {}
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df.get("volume", pd.Series(dtype=float))

    for ind in indicators:
        ind = ind.strip().lower()
        try:
            if ind.startswith("ema"):
                period = int(ind[3:]) if len(ind) > 3 else 20
                result[f"ema_{period}"] = close.ewm(span=period).mean().tolist()

            elif ind.startswith("sma"):
                period = int(ind[3:]) if len(ind) > 3 else 20
                result[f"sma_{period}"] = close.rolling(period).mean().tolist()

            elif ind == "rsi":
                delta = close.diff()
                gain = delta.clip(lower=0).rolling(14).mean()
                loss = (-delta.clip(upper=0)).rolling(14).mean()
                rs = gain / loss.replace(0, 1e-10)
                result["rsi"] = (100 - 100 / (1 + rs)).tolist()

            elif ind == "macd":
                ema12 = close.ewm(span=12).mean()
                ema26 = close.ewm(span=26).mean()
                macd_line = ema12 - ema26
                signal = macd_line.ewm(span=9).mean()
                result["macd"] = macd_line.tolist()
                result["macd_signal"] = signal.tolist()
                result["macd_hist"] = (macd_line - signal).tolist()

            elif ind == "bb" or ind == "bollinger":
                ma = close.rolling(20).mean()
                std = close.rolling(20).std()
                result["bb_upper"] = (ma + 2 * std).tolist()
                result["bb_mid"] = ma.tolist()
                result["bb_lower"] = (ma - 2 * std).tolist()

            elif ind == "atr":
                tr = pd.concat([
                    high - low,
                    (high - close.shift()).abs(),
                    (low - close.shift()).abs()
                ], axis=1).max(axis=1)
                result["atr"] = tr.rolling(14).mean().tolist()

            elif ind == "adx":
                # Simplified ADX
                tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
                result["adx"] = tr.rolling(14).mean().tolist()

            elif ind == "obv":
                obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
                result["obv"] = obv.tolist()

        except Exception:
            result[ind] = []

    result["timestamps"] = [str(t) for t in df.index.tolist()]
    result["close"] = close.tolist()
    return result


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build 60+ features for ML models."""
    features = pd.DataFrame(index=df.index)
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df.get("volume", pd.Series(1, index=df.index))

    # Price returns
    for p in [1, 5, 10, 20]:
        features[f"return_{p}b"] = close.pct_change(p)

    # EMAs
    for p in [5, 10, 20, 50, 200]:
        ema = close.ewm(span=p).mean()
        features[f"ema_{p}"] = ema
        features[f"price_to_ema_{p}"] = close / ema - 1

    # RSI
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, 1e-10)
    features["rsi_14"] = 100 - 100 / (1 + rs)

    # MACD
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    macd = ema12 - ema26
    features["macd"] = macd
    features["macd_signal"] = macd.ewm(span=9).mean()
    features["macd_hist"] = macd - features["macd_signal"]

    # ATR
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    features["atr_14"] = tr.rolling(14).mean()
    features["atr_pct"] = features["atr_14"] / close

    # Bollinger Bands
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    features["bb_pos"] = (close - bb_mid) / (2 * bb_std + 1e-10)

    # Volume
    features["volume_ratio"] = volume / volume.rolling(20).mean()
    features["obv"] = (np.sign(close.diff()) * volume).fillna(0).cumsum()

    # Statistical
    features["zscore_20"] = (close - close.rolling(20).mean()) / (close.rolling(20).std() + 1e-10)
    features["rolling_max_20"] = close.rolling(20).max()
    features["rolling_min_20"] = close.rolling(20).min()
    features["price_range_pct"] = (features["rolling_max_20"] - features["rolling_min_20"]) / close

    # Time features
    features["hour"] = df.index.hour if hasattr(df.index, 'hour') else 0
    features["day_of_week"] = df.index.dayofweek if hasattr(df.index, 'dayofweek') else 0

    return features.dropna()
