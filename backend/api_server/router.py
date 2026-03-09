from fastapi import FastAPI
from .routes import health, agents, market, trading, portfolio, strategies, backtest, broker, ml, alerts
from .websocket_server import websocket_market, websocket_agent, websocket_trades
from fastapi import WebSocket


def register_routes(app: FastAPI):
    # REST routes
    app.include_router(health.router)
    app.include_router(agents.router)
    app.include_router(market.router)
    app.include_router(trading.router)
    app.include_router(portfolio.router)
    app.include_router(strategies.router)
    app.include_router(backtest.router)
    app.include_router(broker.router)
    app.include_router(ml.router)
    app.include_router(alerts.router)

    # WebSocket routes
    app.add_api_websocket_route("/ws/market", websocket_market)
    app.add_api_websocket_route("/ws/agent", websocket_agent)
    app.add_api_websocket_route("/ws/trades", websocket_trades)
