
import numpy as np
import pandas as pd


def calculate_metrics(
    returns: pd.Series,
    trading_days: int = 252,
    risk_free_rate: float = 0.0,
) -> dict:
    """Calculate performance metrics from daily returns."""
    if not isinstance(returns, pd.Series):
        raise TypeError("returns must be a pandas Series")

    if returns.empty:
        raise ValueError("returns cannot be empty")

    if trading_days <= 0:
        raise ValueError("trading_days must be positive")

    if not np.isfinite(returns.to_numpy(dtype=float)).all():
        raise ValueError("returns must be finite")

    if (returns < -1).any():
        raise ValueError("returns cannot be less than -100%")

    total_return = (1 + returns).prod() - 1

    daily_volatility = returns.std(ddof=1)
    annualized_volatility = daily_volatility * np.sqrt(trading_days)

    daily_risk_free_rate = (
        (1 + risk_free_rate) ** (1 / trading_days) - 1
    )

    if pd.isna(daily_volatility) or daily_volatility == 0:
        sharpe_ratio = None
    else:
        sharpe_ratio = (
            (returns.mean() - daily_risk_free_rate)
            / daily_volatility
            * np.sqrt(trading_days)
        )

    equity_curve = (1 + returns).cumprod()

    equity_with_initial = pd.concat(
        [pd.Series([1.0]), equity_curve.reset_index(drop=True)],
        ignore_index=True,
    )

    running_peak = equity_with_initial.cummax()
    drawdown = equity_with_initial / running_peak - 1
    max_drawdown = drawdown.min()

    return {
        "total_return": float(total_return),
        "annualized_volatility": (
            float(annualized_volatility)
            if pd.notna(annualized_volatility)
            else None
        ),
        "sharpe_ratio": (
            float(sharpe_ratio)
            if sharpe_ratio is not None
            else None
        ),
        "max_drawdown": float(max_drawdown),
    }
