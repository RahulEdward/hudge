from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter(prefix="/api/v1/market", tags=["Market"])


@router.get("/quote/{symbol}")
async def get_quote(symbol: str, exchange: str = "NSE"):
    from backend.data_engine.data_cache import get_cache
    cache = get_cache()
    quote = await cache.get_quote(symbol)
    if not quote:
        raise HTTPException(status_code=404, detail=f"No quote available for {symbol}")
    return {"success": True, "symbol": symbol, "quote": quote}


@router.get("/ohlcv/{symbol}")
async def get_ohlcv(
    symbol: str,
    timeframe: str = "1D",
    limit: int = Query(default=100, le=1000),
    exchange: str = "NSE",
):
    from backend.data_engine.historical_loader import get_historical_loader
    loader = get_historical_loader()
    data = await loader.get_ohlcv(symbol, timeframe, limit=limit)
    return {"success": True, "symbol": symbol, "timeframe": timeframe, "data": data}


@router.get("/indicators/{symbol}")
async def get_indicators(symbol: str, timeframe: str = "1D", indicators: str = "ema,rsi,macd"):
    from backend.data_engine.historical_loader import get_historical_loader
    from backend.data_engine.feature_builder import compute_indicators
    loader = get_historical_loader()
    df = await loader.get_dataframe(symbol, timeframe, limit=200)
    ind_list = [i.strip() for i in indicators.split(",")]
    result = compute_indicators(df, ind_list)
    return {"success": True, "symbol": symbol, "indicators": result}
