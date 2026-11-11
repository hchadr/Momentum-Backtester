
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_backtest_endpoint(monkeypatch):
    def fake_load_market_data(symbol, start, end):
        return pd.Series(
            [100.0, 110.0, 121.0, 108.9],
            index=pd.date_range("2023-01-01", periods=4),
        )

    monkeypatch.setattr(
        "app.main.load_market_data",
        fake_load_market_data,
    )

    response = client.post(
        "/api/backtests",
        json={
            "symbol": "AAPL",
            "start": "2023-01-01",
            "end": "2024-01-01",
            "lookback": 1,
            "initial_capital": 10000,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "AAPL"
    assert data["observations"] == 4
    assert data["final_equity"] == pytest.approx(9900.0)
    assert data["strategy_metrics"]["total_return"] == pytest.approx(-0.01)


def test_invalid_dates():
    response = client.post(
        "/api/backtests",
        json={
            "symbol": "AAPL",
            "start": "2024-01-01",
            "end": "2023-01-01",
        },
    )

    assert response.status_code == 422
