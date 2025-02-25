from pydantic_settings import BaseSettings
from datetime import timedelta
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)  # 只输出 INFO 及以上级别的日志

class Settings(BaseSettings):
    DATABASE_URL: str
    BINANCE_WS_URL: str = "wss://ws-fapi.binance.com/ws-fapi/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # 数据库配置
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # 生产环境配置
    PRODUCTION: bool = True
    
    # 性能相关配置
    WORKERS: int = 4
    WORKER_CONNECTIONS: int = 1000
    
    # 监控配置
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"

settings = Settings() 
