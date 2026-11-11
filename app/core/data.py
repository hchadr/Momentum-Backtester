
import pandas as pd
import yfinance as yf


def load_market_data(
    symbol: str,
    start: str,
    end: str,
) -> pd.Series:
    """Download daily adjusted closing prices from Yahoo Finance."""

    if not symbol or not symbol.strip():
        raise ValueError("symbol cannot be empty")

    if pd.Timestamp(start) >= pd.Timestamp(end):
        raise ValueError("start must be before end")

    data = yf.download(
        symbol.strip().upper(),
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
    )

    if data.empty:
        raise ValueError("No market data found for the requested period")

    close = data["Close"]

    # yfinance may return a one-column DataFrame.
    if isinstance(close, pd.DataFrame):
        if close.shape[1] != 1:
            raise ValueError("Expected prices for one symbol")
        close = close.iloc[:, 0]

    close = close.dropna().sort_index()
    close.name = "close"

    if close.empty:
        raise ValueError("No valid closing prices found")

    return close
