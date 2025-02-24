from fastapi import APIRouter, Depends, HTTPException, WebSocket, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import TradingSignal
from ..services.trading_service import TradingService
from ..services.binance_ws import binance_ws
from fastapi.responses import FileResponse
from ..services.image_service import image_service
from ..services.telegram_service import telegram_service
from ..models.trading import TradingSignal as TradingSignalModel
from ..utils.logger import setup_logger
from datetime import datetime
import pytz
from ..services.monitor_service import MonitorService

# 创建路由器时指定前缀
router = APIRouter()
logger = setup_logger("endpoints")

@router.post("/signal")
@MonitorService.monitor_request
async def create_signal(signal: TradingSignal, db: Session = Depends(get_db)):
    """处理交易信号"""
    try:
        logger.info(f"Received signal: {signal.__dict__}")
        result = await TradingService.create_signal(db, signal)
        MonitorService.trade_count.inc()
        if result is None:
            return {"message": "No matching open position found"}
        return result
    except Exception as e:
        logger.error(f"Error handling signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals")
@MonitorService.monitor_request
async def get_signals(db: Session = Depends(get_db)):
    """获取所有交易信号"""
    try:
        return await TradingService.get_all_signals(db)
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def send_strategy_report(signals: List[TradingSignalModel], strategy_name: str, trade_id: str):
    """生成策略报告并发送到 Telegram"""
    try:
        # 生成图片
        image_path = image_service.generate_strategy_image(signals, strategy_name)
        if image_path:
            # 发送到 Telegram
            await telegram_service.send_image(
                image_path,
                caption=f"策略报告: {strategy_name}\n交易ID: {trade_id}"
            )
            logger.info(f"Strategy report sent for trade_id: {trade_id}")
        else:
            logger.error(f"Failed to generate strategy image for trade_id: {trade_id}")
    except Exception as e:
        logger.error(f"Error sending strategy report: {e}")

@router.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await websocket.accept()
    logger = setup_logger("websocket")
    
    async def price_callback(symbol: str, price: float):
        if websocket.client_state.CONNECTED:  # 检查连接状态
            try:
                await websocket.send_json({"symbol": symbol, "price": price})
            except Exception as e:
                logger.error(f"Error sending price update: {str(e)}")
                return False
            return True
        return False

    try:
        binance_ws.add_price_callback(symbol, price_callback)
        
        while True:
            try:
                await websocket.receive_text()  # 保持连接活跃
            except Exception:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        binance_ws.remove_price_callback(symbol, price_callback)

@router.get("/signals/{strategy_name}/image")
async def generate_strategy_image(strategy_name: str, db: Session = Depends(get_db)):
    signals = db.query(TradingSignalModel).filter(TradingSignalModel.title == strategy_name).all()
    if not signals:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    image_path = image_service.generate_strategy_image(signals, strategy_name)
    return FileResponse(image_path)

@router.get("/signals/{title}/history")
async def get_strategy_history(title: str, db: Session = Depends(get_db)):
    """获取策略历史记录"""
    return await TradingService.get_strategy_history(db, title)

@router.get("/signals/statistics")
async def get_signals_statistics(
    start_time: str,
    end_time: str,
    db: Session = Depends(get_db)
):
    """获取时间段内的平仓统计"""
    try:
        # 移除 'Z' 后缀并添加时区信息
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        except ValueError:
            # 如果没有毫秒部分，尝试不同的格式
            start = datetime.strptime(start_time.replace('Z', ''), '%Y-%m-%dT%H:%M:%S')
            end = datetime.strptime(end_time.replace('Z', ''), '%Y-%m-%dT%H:%M:%S')
        
        # 设置为中国时区
        china_tz = pytz.timezone('Asia/Shanghai')
        start = start.astimezone(china_tz)
        end = end.astimezone(china_tz)
        
        logger.info(f"Querying signals between {start} and {end}")
        return await TradingService.get_closed_signals_by_timerange(db, start, end)
    except ValueError as e:
        logger.error(f"Date parsing error: {e}")
        raise HTTPException(status_code=400, detail=str(e)) 