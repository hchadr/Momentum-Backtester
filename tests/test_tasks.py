
from datetime import date

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.db.models import Backtest
from app.tasks import run_backtest_task


@pytest.fixture
def db_session(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    monkeypatch.setattr(
        "app.tasks.SessionLocal",
        TestingSessionLocal,
    )

    with TestingSessionLocal() as db:
        yield db

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def pending_backtest(db_session):
    backtest = Backtest(
        symbol="AAPL",
        start_date=date(2023, 1, 1),
        end_date=date(2024, 1, 1),
        lookback=1,
        initial_capital=10000,
        status="PENDING",
    )

    db_session.add(backtest)
    db_session.commit()
    db_session.refresh(backtest)

    return backtest


def test_task_completes_and_saves_results(
    db_session, pending_backtest, monkeypatch
):
    def fake_load_market_data(symbol, start, end):
        return pd.Series(
            [100.0, 110.0, 121.0, 108.9],
            index=pd.date_range("2023-01-01", periods=4),
        )

    monkeypatch.setattr(
        "app.tasks.load_market_data",
        fake_load_market_data,
    )

    result = run_backtest_task.run(pending_backtest.id)

    db_session.expire_all()

    saved = db_session.get(Backtest, pending_backtest.id)

    assert result["status"] == "COMPLETED"
    assert saved.status == "COMPLETED"

    assert saved.total_return is not None
    assert saved.final_equity is not None
    assert saved.benchmark_final_equity is not None

    assert len(saved.equity_points) == 4


def test_task_marks_failed_on_error(
    db_session, pending_backtest, monkeypatch
):
    def fake_load_market_data(symbol, start, end):
        raise RuntimeError("Market data unavailable")

    monkeypatch.setattr(
        "app.tasks.load_market_data",
        fake_load_market_data,
    )

    with pytest.raises(
        RuntimeError,
        match="Market data unavailable",
    ):
        run_backtest_task.run(pending_backtest.id)

    db_session.expire_all()

    saved = db_session.get(Backtest, pending_backtest.id)

    assert saved.status == "FAILED"
    assert len(saved.equity_points) == 0
