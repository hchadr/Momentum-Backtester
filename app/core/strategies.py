
import pandas as pd


def momentum_positions(
    close: pd.Series,
    lookback: int = 20,
) -> pd.Series:
    """Generate long-or-cash positions using price momentum."""
    if lookback < 1:
        raise ValueError("lookback must be at least 1")

    if not isinstance(close, pd.Series):
        raise TypeError("close must be a pandas Series")

    if close.empty:
        raise ValueError("close cannot be empty")

    momentum = close.pct_change(periods=lookback)

    return (momentum > 0).astype(int).rename("position")
