from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from ..models.trading import TradingSignal as TradingSignalModel
from ..schemas import TradingSignal
from .binance_ws import binance_ws
import logging
import pytz  # 添加时区支持
from sqlalchemy import func, and_

logger = logging.getLogger(__name__)

class TradingService:
    @staticmethod
    async def create_signal(db: Session, signal: TradingSignal) -> TradingSignalModel:
        try:
            china_tz = pytz.timezone('Asia/Shanghai')
            current_time = datetime.now(china_tz)

            if signal.is_close == "1":
                # 查找对应的开仓记录
                open_signal = db.query(TradingSignalModel).filter(
                    TradingSignalModel.trade_id == signal.trade_id,
                    TradingSignalModel.is_close == False
                ).first()
                
                if open_signal:
                    # 获取当前价格作为平仓价格
                    current_price = binance_ws.get_current_price(open_signal.currentcy)
                    logger.info(f"平仓价格: {current_price} for {open_signal.currentcy}")
                    
                    # 更新开仓记录的状态为已平仓
                    open_signal.is_close = True
                    open_signal.closed_at = current_time
                    open_signal.close_price = current_price
                    
                    # 计算获利百分比
                    if open_signal.open_price and current_price:
                        price_change = ((current_price - open_signal.open_price) / open_signal.open_price) * 100
                        # 如果是做空，则收益取反
                        if open_signal.side == 'sell':
                            price_change = -price_change
                        open_signal.profit_percentage = price_change
                        open_signal.is_profit = price_change > 0
                        logger.info(f"获利百分比: {price_change}%")

                        # 更新连胜/连亏
                        last_signal = db.query(TradingSignalModel).filter(
                            TradingSignalModel.title == open_signal.title,
                            TradingSignalModel.id != open_signal.id,
                            TradingSignalModel.is_close == True
                        ).order_by(TradingSignalModel.closed_at.desc()).first()

                        if last_signal:
                            if open_signal.is_profit:
                                if last_signal.is_profit:
                                    open_signal.win_streak = last_signal.win_streak + 1
                                    open_signal.lose_streak = 0
                                else:
                                    open_signal.win_streak = 1
                                    open_signal.lose_streak = 0
                            else:
                                if not last_signal.is_profit:
                                    open_signal.lose_streak = last_signal.lose_streak + 1
                                    open_signal.win_streak = 0
                                else:
                                    open_signal.lose_streak = 1
                                    open_signal.win_streak = 0
                        else:
                            open_signal.win_streak = 1 if open_signal.is_profit else 0
                            open_signal.lose_streak = 0 if open_signal.is_profit else 1

                        logger.info(f"连胜: {open_signal.win_streak}, 连亏: {open_signal.lose_streak}")

                    db.commit()
                    db.refresh(open_signal)
                    return open_signal
                return None

            # 创建新的开仓记录
            current_price = binance_ws.get_current_price(signal.currentcy)
            logger.info(f"开仓价格: {current_price} for {signal.currentcy}")
            
            db_signal = TradingSignalModel(
                trade_id=signal.trade_id,
                title=signal.title,
                currentcy=signal.currentcy,
                zs_tp_trigger_px=float(signal.zs_tp_trigger_px) if signal.zs_tp_trigger_px else None,
                zy_tp_trigger_px=[float(signal.zy_tp_trigger_px)] if signal.zy_tp_trigger_px else None,
                lever=int(signal.lever) if signal.lever else None,
                side=signal.side,
                is_close=False,
                created_at=current_time,
                closed_at=None,
                open_price=current_price,
                close_price=None,
                profit_percentage=None,
                is_profit=None,
                win_streak=0,
                lose_streak=0
            )

            db.add(db_signal)
            db.commit()
            db.refresh(db_signal)
            return db_signal
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing signal: {e}")
            raise

    @staticmethod
    async def get_all_signals(db: Session) -> List[TradingSignalModel]:
        """获取所有交易记录"""
        try:
            # 直接获取所有记录并按时间倒序排序
            signals = db.query(TradingSignalModel).order_by(
                TradingSignalModel.created_at.desc()
            ).all()
            
            # 打印日志以检查数据
            signal_info = [{
                'trade_id': s.trade_id,
                'title': s.title,
                'is_close': s.is_close
            } for s in signals]
            logger.info(f"Retrieved signals: {signal_info}")
            
            # 使用字典保存每个 trade_id 的最新记录
            latest_signals = {}
            for signal in signals:
                if signal.trade_id not in latest_signals:
                    latest_signals[signal.trade_id] = signal
            
            return list(latest_signals.values())
        except Exception as e:
            logger.error(f"Error getting signals: {e}")
            raise

    @staticmethod
    async def get_strategy_history(db: Session, title: str) -> List[TradingSignalModel]:
        """获取单个策略的历史交易记录"""
        try:
            # 获取该策略的所有已平仓记录，按时间倒序排序
            signals = db.query(TradingSignalModel).filter(
                TradingSignalModel.title == title,
                TradingSignalModel.is_close == True
            ).order_by(TradingSignalModel.closed_at.desc()).all()
            
            return signals
        except Exception as e:
            logger.error(f"Error getting strategy history: {e}")
            raise

    @staticmethod
    async def get_closed_signals_by_timerange(db: Session, start_time: datetime, end_time: datetime) -> List[dict]:
        """获取指定时间段内的平仓记录统计"""
        try:
            # 确保使用中国时区
            china_tz = pytz.timezone('Asia/Shanghai')
            if not start_time.tzinfo:
                start_time = china_tz.localize(start_time)
            if not end_time.tzinfo:
                end_time = china_tz.localize(end_time)

            logger.info(f"Searching for closed signals between {start_time} and {end_time}")
            
            # 获取时间段内的所有平仓记录，并按策略名称分组
            signals = db.query(TradingSignalModel).filter(
                TradingSignalModel.is_close == True,
                TradingSignalModel.closed_at >= start_time,
                TradingSignalModel.closed_at <= end_time,
                TradingSignalModel.title.isnot(None)  # 确保有策略名称
            ).order_by(
                TradingSignalModel.title,
                TradingSignalModel.closed_at.desc()
            ).all()

            logger.info(f"Found {len(signals)} signals between {start_time} and {end_time}")
            
            # 按策略名称分组统计
            strategy_stats = {}
            for signal in signals:
                if not signal.title:  # 跳过没有策略名称的记录
                    continue
                
                if signal.title not in strategy_stats:
                    strategy_stats[signal.title] = {
                        'title': signal.title,
                        'close_count': 0,
                        'win_count': 0,
                        'lose_count': 0,
                        'total_profit': 0,
                        'records': []
                    }
                
                stats = strategy_stats[signal.title]
                stats['close_count'] += 1
                if signal.is_profit:
                    stats['win_count'] += 1
                else:
                    stats['lose_count'] += 1
                stats['total_profit'] += signal.profit_percentage or 0
                stats['records'].append({
                    'closed_at': signal.closed_at,
                    'currentcy': signal.currentcy,
                    'profit_percentage': signal.profit_percentage,
                    'open_price': signal.open_price,
                    'close_price': signal.close_price
                })

            # 按平仓次数降序排序
            sorted_stats = sorted(
                strategy_stats.values(),
                key=lambda x: x['close_count'],
                reverse=True
            )

            return sorted_stats

        except Exception as e:
            logger.error(f"Error getting closed signals by timerange: {e}")
            raise 