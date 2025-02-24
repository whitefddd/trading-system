"""recreate trading signals with profit tracking

Revision ID: 202402241234
Revises: 
Create Date: 2024-02-24 12:34:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '202402241234'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('trading_signals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('trade_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('currentcy', sa.String(), nullable=True),
        sa.Column('zs_tp_trigger_px', sa.Float(), nullable=True),
        sa.Column('zy_tp_trigger_px', sa.ARRAY(sa.Float()), nullable=True),
        sa.Column('lever', sa.Integer(), nullable=True),
        sa.Column('side', sa.String(), nullable=True),
        sa.Column('is_close', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('open_price', sa.Float(), nullable=True),
        sa.Column('close_price', sa.Float(), nullable=True),
        sa.Column('profit_percentage', sa.Float(), nullable=True),
        sa.Column('is_profit', sa.Boolean(), nullable=True),
        sa.Column('win_streak', sa.Integer(), default=0),
        sa.Column('lose_streak', sa.Integer(), default=0),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trading_signals_id'), 'trading_signals', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_trading_signals_id'), table_name='trading_signals')
    op.drop_table('trading_signals') 