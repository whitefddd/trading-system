import asyncio
import json
import random
from typing import Dict, Set, Callable
from ..config import settings
from ..utils.logger import setup_logger

class BinanceWebSocket:
    def __init__(self):
        self.connections: Dict[str, Set] = {}
        self.prices: Dict[str, float] = {}
        self.price_callbacks: Dict[str, Set[Callable]] = {}
        self.logger = setup_logger("binance_ws")
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

    async def connect(self, symbol: str):
        """启动价格模拟"""
        if symbol not in self.connections:
            self.connections[symbol] = set()
            self.price_callbacks[symbol] = set()
            
        symbol_upper = symbol.upper()
        if symbol_upper not in self.trends:
            self.trends[symbol_upper] = {
                'direction': random.choice([-1, 1]),  # -1 表示下跌，1 表示上涨
                'strength': random.uniform(0.0001, 0.001),  # 趋势强度
                'steps': 0,  # 当前趋势持续的步数
                'max_steps': random.randint(10, 30)  # 趋势改变前的最大步数
            }
            
        asyncio.create_task(self.simulate_price_updates(symbol))
        self.logger.info(f"Started price simulation for {symbol_upper}")

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
            callbacks = self.price_callbacks.get(symbol, set())
            for callback in callbacks:
                try:
                    await callback(symbol_upper, price)
                except Exception as e:
                    self.logger.error(f"Error in callback for {symbol_upper}: {str(e)}")

    def add_price_callback(self, symbol: str, callback: Callable):
        if symbol not in self.price_callbacks:
            self.price_callbacks[symbol] = set()
        self.price_callbacks[symbol].add(callback)

    def remove_price_callback(self, symbol: str, callback: Callable):
        if symbol in self.price_callbacks:
            self.price_callbacks[symbol].discard(callback)

    async def start_price_updates(self, symbol: str):
        while True:
            try:
                # 生成模拟价格
                price = self.generate_simulated_price(symbol)
                self.current_prices[symbol] = price  # 保存当前价格
                self.logger.info(f"Simulated price for {symbol}: {price}")
                
                # 调用所有回调
                callbacks = self.price_callbacks.get(symbol, [])
                for callback in list(callbacks):
                    if not await callback(symbol, price):
                        callbacks.remove(callback)
                        
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in price updates for {symbol}: {e}")
                await asyncio.sleep(1)

    def get_current_price(self, symbol: str) -> float:
        """获取当前价格"""
        # 如果传入的是 BTC、ETH、XRP 等，需要添加 USDT 后缀
        if not symbol.endswith('USDT'):
            symbol = f"{symbol}USDT"
        symbol = symbol.upper()
        return self.prices.get(symbol)  # 使用 self.prices 而不是 self.current_prices

binance_ws = BinanceWebSocket() 