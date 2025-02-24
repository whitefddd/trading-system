from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 开仓信号 schema
class OpenTradingSignal(BaseModel):
    is_close: str
    trade_id: str
    title: str
    currency: str
    lever_max: Optional[str] = None
    lever_min: Optional[str] = None
    zs_tp_trigger_px: Optional[str] = None
    zy_tp_trigger_px: Optional[str] = None
    lever: Optional[str] = None
    side: Optional[str] = None
    ord_type: Optional[str] = None

# 平仓信号 schema
class CloseTradingSignal(BaseModel):
    is_close: str
    trade_id: str

# 通用交易信号 model
class TradingSignal(BaseModel):
    is_close: str
    trade_id: str
    title: Optional[str] = None
    currentcy: Optional[str] = None
    lever_max: Optional[str] = None
    lever_min: Optional[str] = None
    zs_tp_trigger_px: Optional[str] = None
    zy_tp_trigger_px: Optional[str] = None
    lever: Optional[str] = None
    side: Optional[str] = None
    ord_type: Optional[str] = None
    
    class Config:
        from_attributes = True

# 用户相关的 schema
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" 