# QUANT AI LAB — Broker Gateway Documentation

## Overview

The Broker Gateway provides a unified interface to interact with multiple Indian stock brokers. All broker-specific implementations extend the abstract `BrokerBase` class.

## Supported Brokers

| Broker | Library | Markets |
|--------|---------|---------|
| Angel One | `smartapi-python` | NSE, BSE, MCX |
| Zerodha | `kiteconnect` | NSE, BSE, MCX, CDS |
| Dhan | `dhanhq` | NSE, BSE, MCX |
| Fyers | `fyers-apiv3` | NSE, BSE, MCX |

## Unified Interface (`BrokerBase`)

```python
class BrokerBase(ABC):
    @abstractmethod
    async def login(self, credentials: dict) -> bool
    
    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderResponse
    
    @abstractmethod
    async def modify_order(self, order_id: str, params: dict) -> OrderResponse
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool
    
    @abstractmethod
    async def get_positions(self) -> List[Position]
    
    @abstractmethod
    async def get_holdings(self) -> List[Holding]
    
    @abstractmethod
    async def get_funds(self) -> FundsInfo
    
    @abstractmethod
    async def get_order_book(self) -> List[Order]
    
    @abstractmethod
    async def get_ltp(self, symbol: str) -> float
    
    @abstractmethod
    async def get_historical(self, symbol: str, interval: str, from_date: str, to_date: str) -> pd.DataFrame
```

## Broker Manager

The `BrokerManager` handles:
- Broker registration and selection
- Connection pooling
- Automatic reconnection
- Credential management (encrypted storage)
- Failover between brokers

## Order Types

| Type | Description |
|------|-------------|
| `MARKET` | Execute at current market price |
| `LIMIT` | Execute at specified price or better |
| `SL` | Stop-loss order — triggers at stop price |
| `SL-M` | Stop-loss market — market order at trigger |
| `TP` | Take-profit order |
| `TRAILING` | Trailing stop with dynamic price adjustment |

## Configuration

```yaml
# configs/broker_config.yaml
brokers:
  angel_one:
    enabled: true
    api_key: ""        # Encrypted
    client_id: ""      # Encrypted
    password: ""       # Encrypted
    totp_secret: ""    # Encrypted
    
  zerodha:
    enabled: false
    api_key: ""
    api_secret: ""
    
  dhan:
    enabled: false
    client_id: ""
    access_token: ""
    
  fyers:
    enabled: false
    app_id: ""
    secret_key: ""
```

## Paper Trading Mode

When `mode: "paper"`, the broker gateway routes to the Paper Trading Engine instead of real brokers:
- Simulated order execution with realistic slippage
- Virtual portfolio management
- Performance tracking identical to live mode
