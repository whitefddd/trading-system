import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.trading import Base, TradingSignal
from app.services.trading_service import TradingService
from app.schemas import TradingSignal as TradingSignalSchema
from datetime import datetime, timedelta

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_signal(db_session: Session):
    signal_data = TradingSignalSchema(
        trade_id="test_trade",
        title="test_strategy",
        currentcy="BTCUSDT",
        is_close="0"
    )
    
    result = await TradingService.create_signal(db_session, signal_data)
    assert result is not None
    assert result.trade_id == "test_trade"
    assert result.title == "test_strategy"

def test_get_closed_signals_by_timerange(db_session: Session):
    # 创建测试数据
    now = datetime.now()
    signal = TradingSignal(
        trade_id="test_trade",
        title="test_strategy",
        is_close=True,
        closed_at=now,
        profit_percentage=10.5
    )
    db_session.add(signal)
    db_session.commit()
    
    # 测试查询
    start_time = now - timedelta(days=1)
    end_time = now + timedelta(days=1)
    results = await TradingService.get_closed_signals_by_timerange(
        db_session, start_time, end_time
    )
    
    assert len(results) == 1
    assert results[0]['title'] == "test_strategy"
    assert results[0]['total_profit'] == 10.5 