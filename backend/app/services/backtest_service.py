from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class BacktestService:
    @staticmethod
    async def run_backtest(strategy_id: str, start_date: datetime, end_date: datetime):
        try:
            # 获取历史数据
            historical_data = await DataService.get_historical_data(start_date, end_date)
            
            # 运行回测
            results = []
            for data in historical_data:
                signal = await StrategyService.generate_signal(data)
                if signal:
                    profit = await BacktestService.calculate_profit(signal, data)
                    results.append(profit)
            
            # 计算统计指标
            stats = {
                'total_trades': len(results),
                'win_rate': len([r for r in results if r > 0]) / len(results),
                'avg_profit': np.mean(results),
                'sharpe_ratio': np.mean(results) / np.std(results) if len(results) > 1 else 0
            }
            
            return stats
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            raise 