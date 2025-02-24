from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ARRAY
from ..database import Base

class TradingSignal(Base):
    __tablename__ = "trading_signals"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String)
    title = Column(String)
    currentcy = Column(String)  # 改回 currentcy 以匹配请求
    zs_tp_trigger_px = Column(Float, nullable=True)
    zy_tp_trigger_px = Column(ARRAY(Float), nullable=True)
    lever = Column(Integer, nullable=True)
    side = Column(String, nullable=True)
    is_close = Column(Boolean, default=False)
    created_at = Column(DateTime)
    closed_at = Column(DateTime, nullable=True)
    open_price = Column(Float, nullable=True)  # 开仓价格
    close_price = Column(Float, nullable=True)  # 平仓价格
    profit_percentage = Column(Float, nullable=True)  # 获利百分比
    is_profit = Column(Boolean, nullable=True)  # 是否盈利
    win_streak = Column(Integer, default=0)  # 连胜次数
    lose_streak = Column(Integer, default=0)  # 连亏次数 