from sqlalchemy import Column, Integer, String, Float, JSON, Text, DateTime, func
from .base import Base, TimestampMixin


class BacktestResult(Base, TimestampMixin):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(String(100), unique=True, index=True)
    strategy_id = Column(String(100), index=True)
    symbol = Column(String(50))
    timeframe = Column(String(20))
    start_date = Column(String(20))
    end_date = Column(String(20))
    initial_capital = Column(Float, default=1000000)
    final_capital = Column(Float)
    total_return_pct = Column(Float)
    win_rate = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    calmar_ratio = Column(Float)
    max_drawdown_pct = Column(Float)
    profit_factor = Column(Float)
    expectancy = Column(Float)
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    avg_trade_duration = Column(String(50))
    equity_curve = Column(JSON, default=[])
    monthly_returns = Column(JSON, default={})
    trade_log = Column(JSON, default=[])
    report_html = Column(Text)
    status = Column(String(20), default="completed")
    meta = Column(JSON, default={})
