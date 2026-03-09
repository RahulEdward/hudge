import numpy as np
import pandas as pd
from typing import Dict, Any, List


def compute_metrics(equity_curve: List[float], trades: List[Dict], initial_capital: float) -> Dict[str, Any]:
    """Compute comprehensive backtest performance metrics."""
    if not equity_curve or not trades:
        return {}

    eq = np.array(equity_curve)
    returns = np.diff(eq) / eq[:-1]

    # Basic stats
    total_return = (eq[-1] - initial_capital) / initial_capital * 100
    winning = [t for t in trades if t.get("pnl", 0) > 0]
    losing = [t for t in trades if t.get("pnl", 0) < 0]
    win_rate = len(winning) / len(trades) * 100 if trades else 0

    # Sharpe Ratio (annualized, daily returns)
    mean_return = returns.mean()
    std_return = returns.std() + 1e-10
    sharpe = (mean_return / std_return) * np.sqrt(252)

    # Sortino Ratio
    downside = returns[returns < 0]
    downside_std = downside.std() + 1e-10
    sortino = (mean_return / downside_std) * np.sqrt(252)

    # Max Drawdown
    peak = np.maximum.accumulate(eq)
    drawdown = (eq - peak) / peak * 100
    max_drawdown = drawdown.min()

    # Calmar Ratio
    annual_return = total_return * (252 / max(len(returns), 1))
    calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

    # Profit Factor
    gross_profit = sum(t.get("pnl", 0) for t in winning)
    gross_loss = abs(sum(t.get("pnl", 0) for t in losing))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    # Expectancy
    avg_win = gross_profit / len(winning) if winning else 0
    avg_loss = gross_loss / len(losing) if losing else 0
    expectancy = (win_rate / 100 * avg_win) - ((1 - win_rate / 100) * avg_loss)

    return {
        "total_return_pct": round(total_return, 2),
        "win_rate": round(win_rate, 2),
        "sharpe_ratio": round(sharpe, 3),
        "sortino_ratio": round(sortino, 3),
        "calmar_ratio": round(calmar, 3),
        "max_drawdown_pct": round(max_drawdown, 2),
        "profit_factor": round(profit_factor, 3),
        "expectancy": round(expectancy, 2),
        "total_trades": len(trades),
        "winning_trades": len(winning),
        "losing_trades": len(losing),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "final_capital": round(eq[-1], 2),
    }


def compute_monthly_returns(equity_curve: List[float], dates: List) -> Dict[str, float]:
    """Compute monthly P&L breakdown."""
    if not equity_curve or not dates:
        return {}
    df = pd.DataFrame({"equity": equity_curve}, index=pd.to_datetime(dates))
    monthly = df.resample("ME").last().pct_change() * 100
    return {str(idx.date()): round(val, 2) for idx, val in monthly["equity"].dropna().items()}
