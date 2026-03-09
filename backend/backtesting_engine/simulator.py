import uuid
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger

from .performance_metrics import compute_metrics, compute_monthly_returns


async def run_backtest(
    strategy_id: str,
    symbol: str,
    timeframe: str = "1D",
    start_date: str = None,
    end_date: str = None,
    initial_capital: float = 1000000,
) -> Dict[str, Any]:
    """Run a vectorized backtest for a strategy."""
    result_id = str(uuid.uuid4())[:12]

    # Get historical data
    from backend.data_engine.historical_loader import get_historical_loader
    loader = get_historical_loader()
    df = await loader.get_dataframe(symbol, timeframe, limit=500)

    if df is None or df.empty:
        return {"error": "No historical data available", "result_id": result_id}

    # Filter by date range
    if start_date:
        df = df[df.index >= start_date]
    if end_date:
        df = df[df.index <= end_date]

    if len(df) < 30:
        return {"error": "Insufficient data for backtest (need 30+ bars)", "result_id": result_id}

    # Get strategy entry/exit rules
    strategy = await _load_strategy(strategy_id)
    signals = _generate_signals(df, strategy)

    # Simulate portfolio
    trades, equity_curve = _simulate_portfolio(df, signals, initial_capital)

    # Compute metrics
    metrics = compute_metrics(equity_curve, trades, initial_capital)
    monthly_returns = compute_monthly_returns(equity_curve, df.index.tolist())

    result = {
        "result_id": result_id,
        "strategy_id": strategy_id,
        "symbol": symbol,
        "timeframe": timeframe,
        "start_date": str(df.index[0].date()),
        "end_date": str(df.index[-1].date()),
        "initial_capital": initial_capital,
        "equity_curve": [round(e, 2) for e in equity_curve],
        "trade_log": trades,
        "monthly_returns": monthly_returns,
        **metrics,
    }

    # Save to database
    await _save_result(result)
    logger.info(f"Backtest complete: {result_id} | Return: {metrics.get('total_return_pct')}% | Sharpe: {metrics.get('sharpe_ratio')}")
    return result


def _generate_signals(df: pd.DataFrame, strategy: Dict) -> pd.Series:
    """Generate buy/sell signals from strategy rules."""
    close = df["close"]

    # Default: EMA crossover strategy
    ema_fast = close.ewm(span=strategy.get("parameters", {}).get("ema_fast", 10)).mean()
    ema_slow = close.ewm(span=strategy.get("parameters", {}).get("ema_slow", 30)).mean()

    # Signals: 1=buy, -1=sell, 0=hold
    signals = pd.Series(0, index=df.index)
    signals[ema_fast > ema_slow] = 1
    signals[ema_fast <= ema_slow] = -1

    # RSI filter
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rsi = 100 - 100 / (1 + gain / (loss + 1e-10))
    signals[(rsi > 70) & (signals == 1)] = 0  # Don't buy overbought
    signals[(rsi < 30) & (signals == -1)] = 0  # Don't sell oversold

    return signals


def _simulate_portfolio(df: pd.DataFrame, signals: pd.Series,
                         initial_capital: float) -> tuple:
    """Vectorized portfolio simulation."""
    capital = initial_capital
    position = 0
    entry_price = 0
    trades = []
    equity = []
    commission = 20

    for i, (idx, row) in enumerate(df.iterrows()):
        price = row["close"]
        signal = signals.iloc[i]

        # Entry
        if signal == 1 and position == 0:
            qty = int(capital * 0.95 / price)
            if qty > 0:
                cost = qty * price + commission
                capital -= cost
                position = qty
                entry_price = price

        # Exit
        elif signal == -1 and position > 0:
            proceeds = position * price - commission
            pnl = (price - entry_price) * position - commission * 2
            capital += proceeds
            trades.append({
                "entry_price": round(entry_price, 2),
                "exit_price": round(price, 2),
                "quantity": position,
                "pnl": round(pnl, 2),
                "return_pct": round((price - entry_price) / entry_price * 100, 2),
                "date": str(idx.date()),
            })
            position = 0
            entry_price = 0

        # Equity = cash + position value
        equity.append(capital + position * price)

    return trades, equity


async def _load_strategy(strategy_id: str) -> Dict:
    try:
        from backend.database.connection import get_session
        from backend.database.repositories import StrategyRepository
        async for session in get_session():
            repo = StrategyRepository(session)
            s = await repo.get_by_strategy_id(strategy_id)
            if s:
                return {"parameters": s.parameters or {}, "entry_rules": s.entry_rules or {}}
    except Exception:
        pass
    return {"parameters": {"ema_fast": 10, "ema_slow": 30}}


async def _save_result(result: Dict):
    try:
        from backend.database.connection import get_session
        from backend.database.models.backtest import BacktestResult
        async for session in get_session():
            db_r = BacktestResult(
                result_id=result["result_id"],
                strategy_id=result["strategy_id"],
                symbol=result["symbol"],
                timeframe=result["timeframe"],
                start_date=result["start_date"],
                end_date=result["end_date"],
                initial_capital=result["initial_capital"],
                final_capital=result.get("final_capital"),
                total_return_pct=result.get("total_return_pct"),
                win_rate=result.get("win_rate"),
                sharpe_ratio=result.get("sharpe_ratio"),
                sortino_ratio=result.get("sortino_ratio"),
                calmar_ratio=result.get("calmar_ratio"),
                max_drawdown_pct=result.get("max_drawdown_pct"),
                profit_factor=result.get("profit_factor"),
                expectancy=result.get("expectancy"),
                total_trades=result.get("total_trades"),
                winning_trades=result.get("winning_trades"),
                losing_trades=result.get("losing_trades"),
                equity_curve=result.get("equity_curve", []),
                monthly_returns=result.get("monthly_returns", {}),
                trade_log=result.get("trade_log", []),
                status="completed",
            )
            session.add(db_r)
            await session.commit()
    except Exception as e:
        logger.error(f"Failed to save backtest result: {e}")
