
import pandas as pd

from app.core.strategies import momentum_positions
from app.core.metrics import calculate_metrics

def run_backtest(
    close: pd.Series,
    lookback: int = 20,
    initial_capital: float = 10000.0,
) -> pd.DataFrame:
    """Backtest a daily long-or-cash momentum strategy.

    Signals are generated using closing prices and executed
    with a one-day lag. Assumes zero transaction costs.
    """
    if initial_capital <= 0:
        raise ValueError("initial_capital must be positive")

    if not isinstance(close, pd.Series):
        raise TypeError("close must be a pandas Series")

    if close.empty:
        raise ValueError("close cannot be empty")

    if close.isna().any() or (close <= 0).any():
        raise ValueError("close must contain positive, nonmissing prices")

    if not close.index.is_unique:
        raise ValueError("close index must be unique")

    if not close.index.is_monotonic_increasing:
        raise ValueError("close must be ordered chronologically")

    result = pd.DataFrame(index=close.index)

    result["close"] = close
    result["asset_return"] = close.pct_change().fillna(0.0)

    # Signal is computed after observing the day's close.
    result["signal"] = momentum_positions(close, lookback)

    # Yesterday's signal determines today's exposure.
    result["position"] = result["signal"].shift(1).fillna(0).astype(int)

    result["strategy_return"] = (
        result["position"] * result["asset_return"]
    )

    result["equity"] = (
        initial_capital
        * (1 + result["strategy_return"]).cumprod()
    )

    result["benchmark_equity"] = (
        initial_capital
        * (1 + result["asset_return"]).cumprod()
    )

    return result


def run_backtest_with_metrics(
    close: pd.Series,
    lookback: int = 20,
    initial_capital: float = 10000.0,
) -> dict:
    """Run a momentum backtest and calculate performance metrics."""

    result = run_backtest(
        close=close,
        lookback=lookback,
        initial_capital=initial_capital,
    )

    strategy_metrics = calculate_metrics(
        result["strategy_return"]
    )

    benchmark_metrics = calculate_metrics(
        result["asset_return"]
    )

    return {
        "results": result,
        "strategy_metrics": strategy_metrics,
        "benchmark_metrics": benchmark_metrics,
    }

