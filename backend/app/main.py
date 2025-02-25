from fastapi import FastAPI, Request, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import time
from .config import settings
from .api import endpoints
from .database import engine, Base, get_db
from .middleware.error_handler import error_handler_middleware, validation_exception_handler
import asyncio
from .services.binance_ws import binance_ws, BinanceWebSocket
from .utils.logger import setup_logger
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_redoc_html,
)
from prometheus_client import make_asgi_app
# from .middleware.auth_middleware import auth_middleware
import logging
from fastapi import WebSocketDisconnect

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trading System API",
    description="Advanced trading system with risk management and ML capabilities",
    version="2.0.0",
    docs_url=None,
    redoc_url=None
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 性能监控中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request processed in {process_time:.4f} seconds")
    return response

# 错误处理中间件
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Global error: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error"}
        )

# 添加认证中间件
# app.middleware("http")(auth_middleware)

# 添加重试逻辑
def init_db(retries=5, delay=2):
    for i in range(retries):
        try:
            print(f"尝试连接数据库: {settings.DATABASE_URL}")
            Base.metadata.create_all(bind=engine)
            logger.info("数据库表创建成功")
            return
        except Exception as e:
            print(f"详细错误信息: {str(e)}")
            logger.error(f"数据库初始化失败 (尝试 {i+1}/{retries}): {e}")
            if i < retries - 1:
                time.sleep(delay)
    raise Exception("数据库初始化失败，已达到最大重试次数")

# 创建数据库表
init_db()

# 注册路由
app.include_router(endpoints.router, prefix="/api")

# 在其他导入语句后添加
app.mount("/static", StaticFiles(directory="static"), name="static")

# 添加 metrics 端点
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting application...")
    # 启动 WebSocket 连接
    global binance_ws
    binance_ws = BinanceWebSocket()
    asyncio.create_task(binance_ws.start())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Trading System API",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket client connected")
    try:
        await binance_ws.register(websocket)
        logger.info("WebSocket client registered for price updates")
        while True:
            try:
                # 保持连接活跃
                data = await websocket.receive_text()
                logger.info(f"Received message from client: {data}")
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected")
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    except Exception as e:
        logger.error(f"Error in websocket endpoint: {e}")
    finally:
        logger.info("Unregistering WebSocket client")
        await binance_ws.unregister(websocket) 