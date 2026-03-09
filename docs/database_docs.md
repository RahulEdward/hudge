# QUANT AI LAB — Database Documentation

## Overview

The platform uses a multi-database architecture:
- **SQLite**: Primary local storage (zero-config)
- **PostgreSQL**: Optional for multi-user deployment
- **Redis**: Caching, message queues, real-time data
- **Vector DB**: Agent memory and semantic search (ChromaDB)

## Database Schema

### trades
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| symbol | VARCHAR | Trading instrument |
| side | ENUM | BUY / SELL |
| order_type | ENUM | MARKET / LIMIT / SL / SL-M |
| quantity | INTEGER | Order quantity |
| price | DECIMAL | Order price |
| executed_price | DECIMAL | Fill price |
| status | ENUM | PENDING / EXECUTED / CANCELLED / REJECTED |
| broker | VARCHAR | Broker name |
| mode | ENUM | live / paper |
| strategy_id | UUID | FK to strategies |
| pnl | DECIMAL | Realized P&L |
| created_at | TIMESTAMP | Order creation time |
| executed_at | TIMESTAMP | Execution time |

### strategies
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR | Strategy name |
| description | TEXT | AI-generated description |
| entry_rules | JSON | Entry conditions |
| exit_rules | JSON | Exit conditions |
| indicators | JSON | Technical indicators used |
| parameters | JSON | Strategy parameters |
| status | ENUM | discovered / backtested / approved / rejected / live |
| created_at | TIMESTAMP | Discovery time |

### backtest_results
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| strategy_id | UUID | FK to strategies |
| symbol | VARCHAR | Tested symbol |
| start_date | DATE | Backtest start |
| end_date | DATE | Backtest end |
| win_rate | DECIMAL | Win percentage |
| sharpe_ratio | DECIMAL | Sharpe ratio |
| max_drawdown | DECIMAL | Maximum drawdown |
| profit_factor | DECIMAL | Profit factor |
| expectancy | DECIMAL | Expected value per trade |
| total_trades | INTEGER | Number of trades |
| net_profit | DECIMAL | Net profit/loss |
| equity_curve | JSON | Equity curve data |
| trade_log | JSON | Individual trade log |
| created_at | TIMESTAMP | Backtest run time |

### portfolio
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| symbol | VARCHAR | Instrument |
| quantity | INTEGER | Current quantity |
| avg_price | DECIMAL | Average entry price |
| current_price | DECIMAL | Latest price |
| pnl | DECIMAL | Unrealized P&L |
| pnl_pct | DECIMAL | P&L percentage |

### ml_models
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR | Model name |
| model_type | VARCHAR | XGBoost / LightGBM / LSTM / etc. |
| version | VARCHAR | Model version |
| metrics | JSON | Evaluation metrics |
| file_path | VARCHAR | Serialized model path |
| status | ENUM | training / active / archived |
| created_at | TIMESTAMP | Training time |

### conversations
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| source | ENUM | desktop / telegram / whatsapp |
| user_id | VARCHAR | User identifier |
| message | TEXT | User message |
| response | TEXT | Agent response |
| agent | VARCHAR | Responding agent name |
| intent | VARCHAR | Detected intent |
| created_at | TIMESTAMP | Message time |

### alerts
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| type | VARCHAR | Alert type |
| message | TEXT | Alert message |
| severity | ENUM | info / warning / critical |
| channels | JSON | Delivery channels |
| delivered | BOOLEAN | Delivery status |
| created_at | TIMESTAMP | Alert time |

## Repository Pattern

Each table has a corresponding repository class:

```python
class TradeRepository:
    async def create(self, trade: TradeCreate) -> Trade
    async def get_by_id(self, id: str) -> Trade
    async def list_all(self, filters: dict) -> List[Trade]
    async def update(self, id: str, data: dict) -> Trade
    async def delete(self, id: str) -> bool
```

## Migrations

Using Alembic for schema migrations:

```bash
cd database
alembic init migrations
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```
