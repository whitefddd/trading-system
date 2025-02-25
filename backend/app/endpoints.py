from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_async_session
from .models import TradingSignal
from .services.binance_ws import binance_ws

router = APIRouter()

@router.get("/signals")
async def get_signals():
    async with get_async_session() as session:
        result = await session.execute(
            select(TradingSignal).order_by(TradingSignal.created_at.desc())
        )
        signals = result.scalars().all()
        return signals 

@router.post("/signal")
async def receive_signal(signal: dict):
    # 提取 currentcy
    currentcy = signal.get("currentcy")
    if not currentcy:
        raise HTTPException(status_code=400, detail="currentcy is required")

    # 将 currentcy 转换为 USDT 交易对
    trading_pair = f"{currentcy.upper()}USDT"  # 确保转换为大写并加上 USDT 后缀

    # 动态订阅交易对
    await binance_ws.subscribe_symbol(trading_pair)

    # 查询当前价格
    price = binance_ws.get_current_price(trading_pair)
    if price is None:
        raise HTTPException(status_code=404, detail=f"Price not found for {trading_pair}")

    # 处理开仓逻辑
    # 这里可以添加你的开仓逻辑代码

    return {"message": "Signal received", "price": price} 