"""Initial backtest schema

Revision ID: e69f6c156185
Revises: 
Create Date: 2026-11-11 20:46:21.957699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e69f6c156185'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "backtests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("lookback", sa.Integer(), nullable=False),
        sa.Column("initial_capital", sa.Float(), nullable=False),
        sa.Column("total_return", sa.Float(), nullable=False),
        sa.Column("sharpe_ratio", sa.Float(), nullable=True),
        sa.Column("annualized_volatility", sa.Float(), nullable=True),
        sa.Column("max_drawdown", sa.Float(), nullable=False),
        sa.Column("final_equity", sa.Float(), nullable=False),
        sa.Column("benchmark_final_equity", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "equity_points",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "backtest_id",
            sa.Integer(),
            sa.ForeignKey("backtests.id"),
            nullable=False,
        ),
        sa.Column("trading_date", sa.Date(), nullable=False),
        sa.Column("equity", sa.Float(), nullable=False),
        sa.Column("benchmark_equity", sa.Float(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
    )

    op.create_index(
        "ix_equity_points_backtest_id",
        "equity_points",
        ["backtest_id"],
    )


def downgrade():
    op.drop_index(
        "ix_equity_points_backtest_id",
        table_name="equity_points",
    )
    op.drop_table("equity_points")
    op.drop_table("backtests")
