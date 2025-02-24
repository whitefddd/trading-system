from prometheus_client import Counter, Histogram
import time
from functools import wraps
from ..utils.logger import setup_logger

logger = setup_logger("monitor_service")

class MonitorService:
    # 定义监控指标
    request_count = Counter('http_requests_total', 'Total HTTP requests')
    request_latency = Histogram('http_request_duration_seconds', 'HTTP request latency')
    error_count = Counter('error_total', 'Total errors')
    trade_count = Counter('trade_signals_total', 'Total trade signals')
    
    @staticmethod
    def monitor_request(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                MonitorService.request_count.inc()
                return result
            except Exception as e:
                MonitorService.error_count.inc()
                logger.error(f"Request error: {e}")
                raise
            finally:
                MonitorService.request_latency.observe(time.time() - start_time)
        return wrapper 