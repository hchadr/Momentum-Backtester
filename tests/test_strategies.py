
import pandas as pd
import pytest

from app.core.strategies import momentum_positions


def test_momentum_positions():
    close = pd.Series([100, 110, 105, 120, 115])

    result = momentum_positions(close, lookback=1)

    assert result.tolist() == [0, 1, 0, 1, 0]


def test_lookback_two():
    close = pd.Series([100, 110, 105, 120, 115])

    result = momentum_positions(close, lookback=2)

    assert result.tolist() == [0, 0, 1, 1, 1]


def test_invalid_lookback():
    close = pd.Series([100, 110, 120])

    with pytest.raises(ValueError):
        momentum_positions(close, lookback=0)
