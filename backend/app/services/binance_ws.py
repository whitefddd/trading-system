import asyncio
import json
import random
from typing import Dict, Set, Callable
from ..config import settings
from ..utils.logger import setup_logger
import websockets
import logging

logger = logging.getLogger("binance_ws")

class BinanceWebSocket:
    def __init__(self):
        # 基础交易对
        self.base_symbols = ["BTC", "ETH", "XRP", "SOL", "RUNE", "1000PEPE", "W"]
        # 转换为 USDT 交易对
        self.symbols = [f"{symbol}USDT".lower() for symbol in self.base_symbols]
        self.ws = None
        self.prices = {}
        self.logger = setup_logger("binance_ws")
        self.connected_clients = set()
        # 初始化基准价格
        self.base_prices = {
            'BTCUSDT': 52000.0,
            'ETHUSDT': 3200.0,
            'XRPUSDT': 0.55
        }
        # 记录每个交易对的趋势
        self.trends = {}
        # 修改更新间隔为1秒
        self.update_interval = 1
        self.current_prices = {}  # 添加存储当前价格的字典
        self.latest_prices = {}

    async def connect(self):
        """建立 WebSocket 连接"""
        while True:
            try:
                self.ws = await websockets.connect('wss://fstream.binance.com/ws')
                self.logger.info("Connected to Binance WebSocket")
                
                # 订阅所有交易对的标记价格更新
                subscription = {
                    "method": "SUBSCRIBE",
                    "params": [f"{symbol}@markPrice@1s" for symbol in self.symbols],
                    "id": 1
                }
                
                await self.ws.send(json.dumps(subscription))
                self.logger.info("Subscription sent")
                
                # 开始接收消息
                await self.receive_messages()
                
            except websockets.exceptions.ConnectionClosed:
                self.logger.error("Binance WebSocket connection closed")
            except Exception as e:
                self.logger.error(f"Connection error: {e}")
            
            # 重连前等待
            await asyncio.sleep(5)
            self.logger.info("Attempting to reconnect...")

    async def receive_messages(self):
        while True:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                self.logger.debug(f"Received message: {data}")

                if 's' in data and 'p' in data:
                    symbol = data['s']
                    price = float(data['p'])
                    self.prices[symbol] = price

                    # 只在接收到开仓信号或平仓信号时输出价格日志
                    if 'is_close' in data or 'trade_id' in data:
                        self.logger.info(f"Price updated for {symbol}: {price}")

                    # 广播价格更新给所有连接的客户端
                    for client in self.connected_clients.copy():
                        try:
                            message = {
                                's': symbol,
                                'p': str(price)
                            }
                            await client.send_json(message)
                            self.logger.debug(f"Successfully sent price update to client: {symbol}={price}")
                        except Exception as e:
                            self.logger.error(f"Failed to send price update to client: {e}")
                            self.connected_clients.remove(client)
            except Exception as e:
                self.logger.error(f"Error in receive_messages: {e}")
                break

    async def register(self, websocket):
        self.connected_clients.add(websocket)
        self.logger.info(f"Client registered, total clients: {len(self.connected_clients)}")
        self.logger.info("Sending initial prices to new client")
        # 发送当前价格
        for symbol, price in self.prices.items():
            try:
                message = {
                    's': symbol,
                    'p': str(price)
                }
                self.logger.info(f"Sending initial message to client: {message}")
                await websocket.send_json(message)
                self.logger.info(f"Sent initial price to new client: {symbol}={price}")
            except Exception as e:
                self.logger.error(f"Error sending initial price: {e}")
                self.connected_clients.remove(websocket)
                raise  # 重新抛出异常，让上层处理连接问题

    async def unregister(self, websocket):
        self.connected_clients.remove(websocket)

    async def start(self):
        """启动 WebSocket 服务"""
        while True:
            try:
                await self.connect()
            except Exception as e:
                self.logger.error(f"Connection error in start: {e}")
            await asyncio.sleep(5)  # 重连间隔

    def get_current_price(self, symbol: str) -> float:
        """获取当前价格"""
        # 移除可能存在的 USDT 后缀
        symbol = symbol.upper().replace('USDT', '')
        # 添加 USDT 后缀并转换为大写
        symbol = f"{symbol}USDT".upper()
        
        price = self.prices.get(symbol)
        if price is None:
            self.logger.warning(f"No price found for {symbol}")
        return price

    async def simulate_price_updates(self, symbol: str):
        """模拟价格更新"""
        symbol_upper = symbol.upper()
        while True:
            try:
                # 更新趋势
                trend = self.trends[symbol_upper]
                trend['steps'] += 1
                if trend['steps'] >= trend['max_steps']:
                    trend['direction'] = -trend['direction']
                    trend['strength'] = random.uniform(0.0001, 0.001)
                    trend['steps'] = 0
                    trend['max_steps'] = random.randint(10, 30)

                # 生成价格波动
                base_price = self.base_prices[symbol_upper]
                trend_change = trend['direction'] * trend['strength']
                random_change = random.uniform(-0.0005, 0.0005)
                total_change = trend_change + random_change

                # 更新价格
                self.base_prices[symbol_upper] *= (1 + total_change)
                
                # 确保价格在合理范围内
                if symbol_upper == 'BTCUSDT':
                    self.base_prices[symbol_upper] = max(min(self.base_prices[symbol_upper], 55000), 49000)
                elif symbol_upper == 'ETHUSDT':
                    self.base_prices[symbol_upper] = max(min(self.base_prices[symbol_upper], 3500), 2900)
                elif symbol_upper == 'XRPUSDT':
                    self.base_prices[symbol_upper] = max(min(self.base_prices[symbol_upper], 0.65), 0.45)

                # 保存并广播价格
                self.prices[symbol_upper] = round(self.base_prices[symbol_upper], 8)
                self.logger.info(f"Simulated price for {symbol_upper}: {self.prices[symbol_upper]}")
                await self.broadcast_price(symbol)
                
                await asyncio.sleep(self.update_interval)  # 每1秒更新一次
                
            except Exception as e:
                self.logger.error(f"Error in price simulation for {symbol_upper}: {e}")
                await asyncio.sleep(self.update_interval)

    async def broadcast_price(self, symbol: str):
        symbol_upper = symbol.upper()
        if symbol_upper in self.prices:
            price = self.prices[symbol_upper]
            callbacks = self.callbacks
            for callback in callbacks:
                try:
                    await callback(symbol_upper, price)
                except Exception as e:
                    self.logger.error(f"Error in callback for {symbol_upper}: {str(e)}")

    def add_price_callback(self, symbol: str, callback: Callable):
        if symbol not in self.callbacks:
            self.callbacks.append(callback)

    def remove_price_callback(self, symbol: str, callback: Callable):
        if symbol in self.callbacks:
            self.callbacks.remove(callback)

    async def start_price_updates(self, symbol: str):
        while True:
            try:
                # 生成模拟价格
                price = self.generate_simulated_price(symbol)
                self.current_prices[symbol] = price  # 保存当前价格
                self.logger.info(f"Simulated price for {symbol}: {price}")
                
                # 调用所有回调
                callbacks = self.callbacks
                for callback in list(callbacks):
                    if not await callback(symbol, price):
                        callbacks.remove(callback)
                        
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in price updates for {symbol}: {e}")
                await asyncio.sleep(1)

    async def subscribe_symbol(self, symbol: str):
        """动态订阅交易对"""
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            subscription = {
                "method": "SUBSCRIBE",
                "params": [f"{symbol}@markPrice@1s"],
                "id": 1
            }
            await self.ws.send(json.dumps(subscription))
            self.logger.info(f"Subscribed to {symbol} mark price updates.")

binance_ws = BinanceWebSocket() 