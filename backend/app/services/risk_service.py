from typing import List
import numpy as np

class RiskService:
    @staticmethod
    async def check_risk_limits(signal: dict) -> bool:
        try:
            # 检查持仓限制
            total_position = await RiskService.get_total_position()
            if total_position + signal['amount'] > settings.MAX_POSITION:
                return False
            
            # 检查亏损限制
            daily_loss = await RiskService.get_daily_loss()
            if daily_loss < settings.MAX_DAILY_LOSS:
                return False
            
            # 检查风险敞口
            exposure = await RiskService.calculate_exposure(signal)
            if exposure > settings.MAX_EXPOSURE:
                return False
                
            return True
        except Exception as e:
            logger.error(f"Risk check failed: {e}")
            return False 