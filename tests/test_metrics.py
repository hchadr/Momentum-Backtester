
import pandas as pd
import pytest

from app.core.metrics import calculate_metrics
from app.core.engine import run_backtest_with_metrics


def test_total_return():
    returns = pd.Series([0.10, -0.10])

    metrics = calculate_metrics(returns)

    assert metrics["total_return"] == pytest.approx(-0.01)


def test_max_drawdown():
    returns = pd.Series([0.10, -0.20, 0.05])

    metrics = calculate_metrics(returns)

    assert metrics["max_drawdown"] == pytest.approx(-0.20)


def test_zero_volatility():
    returns = pd.Series([0.0, 0.0, 0.0])

    metrics = calculate_metrics(returns)

    assert metrics["sharpe_ratio"] is None
    assert metrics["annualized_volatility"] == 0.0


def test_backtest_with_metrics():
    close = pd.Series([100.0, 110.0, 121.0, 108.9])

    output = run_backtest_with_metrics(
        close,
        lookback=1,
    )

    assert "results" in output
    assert "strategy_metrics" in output
    assert "benchmark_metrics" in output

    assert output["strategy_metrics"]["total_return"] == (
        pytest.approx(-0.01)
    )


def test_invalid_returns():
    returns = pd.Series([0.10, -1.20])

    with pytest.raises(ValueError):
        calculate_metrics(returns)
