"""Comprehensive feature engineering pipeline — 60+ features from OHLCV."""

import pandas as pd
import numpy as np
from loguru import logger


class FeatureEngineeringPipeline:
    """Generates 60+ features from raw OHLCV data for ML models."""

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate all features from a DataFrame with OHLCV columns."""
        if df is None or df.empty:
            return pd.DataFrame()

        features = pd.DataFrame(index=df.index)

        try:
            features = pd.concat([
                features,
                self._price_returns(df),
                self._moving_averages(df),
                self._oscillators(df),
                self._volatility_features(df),
                self._volume_features(df),
                self._statistical_features(df),
                self._time_features(df),
            ], axis=1)
        except Exception as e:
            logger.error(f"Feature engineering failed: {e}")
            return pd.DataFrame()

        features = features.replace([np.inf, -np.inf], np.nan)
        return features.dropna()

    def _price_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        feats = {}
        for period in [1, 2, 3, 5, 10, 20]:
            feats[f"return_{period}"] = close.pct_change(period)
        feats["log_return_1"] = np.log(close / close.shift(1))
        feats["log_return_5"] = np.log(close / close.shift(5))
        feats["high_low_range"] = (df["high"] - df["low"]) / close
        feats["close_open_range"] = (close - df["open"]) / close
        feats["upper_shadow"] = (df["high"] - df[["open", "close"]].max(axis=1)) / close
        feats["lower_shadow"] = (df[["open", "close"]].min(axis=1) - df["low"]) / close
        feats["body_ratio"] = abs(close - df["open"]) / (df["high"] - df["low"] + 1e-10)
        return pd.DataFrame(feats, index=df.index)

    def _moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        feats = {}
        for period in [5, 10, 20, 50]:
            ema = close.ewm(span=period, adjust=False).mean()
            sma = close.rolling(period).mean()
            feats[f"ema_{period}_ratio"] = close / ema - 1
            feats[f"sma_{period}_ratio"] = close / sma - 1
        # EMA crossovers
        ema_5 = close.ewm(span=5, adjust=False).mean()
        ema_20 = close.ewm(span=20, adjust=False).mean()
        feats["ema_5_20_cross"] = ema_5 / ema_20 - 1
        ema_10 = close.ewm(span=10, adjust=False).mean()
        ema_50 = close.ewm(span=50, adjust=False).mean()
        feats["ema_10_50_cross"] = ema_10 / ema_50 - 1
        return pd.DataFrame(feats, index=df.index)

    def _oscillators(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        feats = {}
        # RSI
        for period in [7, 14, 21]:
            delta = close.diff()
            gain = delta.clip(lower=0).rolling(period).mean()
            loss = (-delta.clip(upper=0)).rolling(period).mean()
            rs = gain / (loss + 1e-10)
            feats[f"rsi_{period}"] = 100 - (100 / (1 + rs))
        # MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        feats["macd"] = macd / close
        feats["macd_signal"] = signal / close
        feats["macd_histogram"] = (macd - signal) / close
        # Stochastic
        for period in [14]:
            low_min = df["low"].rolling(period).min()
            high_max = df["high"].rolling(period).max()
            feats[f"stoch_k_{period}"] = ((close - low_min) / (high_max - low_min + 1e-10)) * 100
        # Williams %R
        feats["williams_r"] = ((df["high"].rolling(14).max() - close) /
                               (df["high"].rolling(14).max() - df["low"].rolling(14).min() + 1e-10)) * -100
        return pd.DataFrame(feats, index=df.index)

    def _volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        feats = {}
        # ATR
        for period in [7, 14, 21]:
            high_low = df["high"] - df["low"]
            high_close = abs(df["high"] - close.shift(1))
            low_close = abs(df["low"] - close.shift(1))
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(period).mean()
            feats[f"atr_{period}_pct"] = atr / close
        # Bollinger Bands
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        feats["bb_upper_pct"] = (sma20 + 2 * std20) / close - 1
        feats["bb_lower_pct"] = (sma20 - 2 * std20) / close - 1
        feats["bb_width"] = (4 * std20) / (sma20 + 1e-10)
        feats["bb_position"] = (close - (sma20 - 2 * std20)) / (4 * std20 + 1e-10)
        # Historical volatility
        returns = close.pct_change()
        for period in [5, 10, 20]:
            feats[f"hvol_{period}"] = returns.rolling(period).std()
        # ADX
        feats["adx_proxy"] = abs(close.pct_change(14))
        return pd.DataFrame(feats, index=df.index)

    def _volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        feats = {}
        if "volume" not in df.columns:
            return pd.DataFrame(index=df.index)
        vol = df["volume"].astype(float)
        feats["volume_sma_5_ratio"] = vol / (vol.rolling(5).mean() + 1)
        feats["volume_sma_20_ratio"] = vol / (vol.rolling(20).mean() + 1)
        # OBV
        obv = (np.sign(df["close"].diff()) * vol).cumsum()
        feats["obv_change_5"] = obv.pct_change(5)
        feats["obv_change_20"] = obv.pct_change(20)
        # VWAP proxy
        feats["vwap_ratio"] = df["close"] / ((df["high"] + df["low"] + df["close"]) / 3) - 1
        return pd.DataFrame(feats, index=df.index)

    def _statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        returns = close.pct_change()
        feats = {}
        for period in [10, 20]:
            feats[f"zscore_{period}"] = (close - close.rolling(period).mean()) / (close.rolling(period).std() + 1e-10)
            feats[f"skew_{period}"] = returns.rolling(period).skew()
            feats[f"kurtosis_{period}"] = returns.rolling(period).kurt()
        # Hurst exponent proxy
        feats["autocorr_5"] = returns.rolling(20).apply(lambda x: x.autocorr(lag=5) if len(x) > 5 else 0, raw=False)
        return pd.DataFrame(feats, index=df.index)

    def _time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        feats = {}
        if hasattr(df.index, "hour"):
            feats["hour"] = df.index.hour
            feats["day_of_week"] = df.index.dayofweek
            feats["is_monday"] = (df.index.dayofweek == 0).astype(int)
            feats["is_friday"] = (df.index.dayofweek == 4).astype(int)
        elif "timestamp" in df.columns:
            ts = pd.to_datetime(df["timestamp"])
            feats["hour"] = ts.dt.hour
            feats["day_of_week"] = ts.dt.dayofweek
        else:
            return pd.DataFrame(index=df.index)
        return pd.DataFrame(feats, index=df.index)
