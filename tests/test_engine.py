
import pandas as pd
import pytest

from app.core.engine import run_backtest


def test_backtest_returns():
    close = pd.Series([100.0, 110.0, 121.0, 108.9])

    result = run_backtest(
        close,
        lookback=1,
        initial_capital=10000,
    )

    # Day 1: no position.
    # Day 2: signal turns long, but position is still cash.
    # Day 3: long, earning a 10% return.
    # Day 4: long, losing 10%.
    assert result["position"].tolist() == [0, 0, 1, 1]

    assert result["strategy_return"].iloc[2] == pytest.approx(0.10)
    assert result["strategy_return"].iloc[3] == pytest.approx(-0.10)

    assert result["equity"].iloc[-1] == pytest.approx(9900.0)


def test_constant_prices():
    close = pd.Series([100.0, 100.0, 100.0, 100.0])

    result = run_backtest(close, lookback=1)

    assert (result["strategy_return"] == 0).all()
    assert (result["equity"] == 10000).all()


def test_invalid_capital():
    close = pd.Series([100.0, 110.0, 120.0])

    with pytest.raises(ValueError):
        run_backtest(close, initial_capital=-100)


def test_invalid_prices():
    close = pd.Series([100.0, -10.0, 120.0])

    with pytest.raises(ValueError):
        run_backtest(close)
