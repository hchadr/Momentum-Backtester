
from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.core.data import load_market_data
from app.core.engine import run_backtest_with_metrics


app = FastAPI(
    title="Momentum Backtesting API",
    version="0.1.0",
)


class BacktestRequest(BaseModel):
    symbol: str = Field(min_length=1)
    start: date
    end: date
    lookback: int = Field(default=20, ge=1)
    initial_capital: float = Field(default=10000, gt=0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/backtests")
def create_backtest(request: BacktestRequest):
    if request.start >= request.end:
        raise HTTPException(
            status_code=422,
            detail="start must be before end",
        )

    try:
        close = load_market_data(
            symbol=request.symbol,
            start=request.start.isoformat(),
            end=request.end.isoformat(),
        )

        output = run_backtest_with_metrics(
            close=close,
            lookback=request.lookback,
            initial_capital=request.initial_capital,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    results = output["results"]

    return {
        "symbol": request.symbol.upper(),
        "start": request.start,
        "end": request.end,
        "lookback": request.lookback,
        "initial_capital": request.initial_capital,
        "observations": len(results),
        "strategy_metrics": output["strategy_metrics"],
        "benchmark_metrics": output["benchmark_metrics"],
        "final_equity": float(results["equity"].iloc[-1]),
        "benchmark_final_equity": float(
            results["benchmark_equity"].iloc[-1]
        ),
    }
