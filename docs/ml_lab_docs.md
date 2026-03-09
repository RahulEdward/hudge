# QUANT AI LAB — Machine Learning Lab Documentation

## Overview

The ML Lab is a Quant Research module that automatically generates features, trains models, evaluates signals, and stores models. No manual ML required — agents use it autonomously.

## Models

### 1. Auto Trend Prediction Model
- **Algorithm**: XGBoost / LightGBM ensemble
- **Target**: Next-bar direction (up/down/flat)
- **Features**: 60+ technical features
- **Retraining**: Daily or on-demand

### 2. Regime Detection Model
- **Algorithm**: Hidden Markov Model + K-Means clustering
- **Regimes**: Trending, Mean-Reverting, High-Volatility, Low-Volatility
- **Output**: Current regime label + transition probabilities

### 3. Volatility Forecast Model
- **Algorithm**: GARCH + LightGBM hybrid
- **Target**: Next-N-bar realized volatility
- **Use**: Dynamic position sizing, option pricing signals

### 4. Alpha Discovery Engine
- **Algorithm**: Genetic programming + feature importance ranking
- **Process**: Generate candidate signals → backtest → rank by Sharpe → select top-N
- **Output**: Alpha signals with confidence scores

## Feature Engineering Engine

### Price Features
- Returns (1, 5, 10, 20 bar)
- Log returns
- Price momentum
- Rate of change

### Technical Features
- EMA (9, 21, 50, 200)
- RSI (14)
- MACD (12, 26, 9)
- Bollinger Bands (20, 2)
- ATR (14)
- ADX (14)
- Supertrend
- VWAP

### Volume Features
- Volume SMA ratio
- OBV (On-Balance Volume)
- Volume profile

### Statistical Features
- Rolling mean, std, skewness, kurtosis
- Z-score
- Hurst exponent
- Rolling correlation

### Time Features
- Hour, day of week, month
- Time to expiry (for derivatives)
- Session (pre-market, market, post-market)

## Model Storage

```
ml_lab/
├── storage/
│   ├── models/           # Serialized model files (.pkl, .pt)
│   ├── features/         # Feature pipeline configs
│   ├── evaluations/      # Performance logs
│   └── model_registry.json  # Version tracking
```

## Training Pipeline

```
Raw Data → Feature Engineering → Train/Test Split → Model Training 
    → Evaluation → Model Registry → Deployment to Agents
```

## Evaluation Metrics
- Accuracy, Precision, Recall, F1
- Directional accuracy
- Profit factor (when converted to signals)
- Information coefficient (IC)
- Sharpe ratio of signal returns
