import json
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.trading import TradingSignal as TradingSignalModel
from ..config import settings
from ..utils.logger import setup_logger

logger = setup_logger("backup_service")

class BackupService:
    @staticmethod
    async def backup_database(db: Session):
        try:
            # 确保备份目录存在
            os.makedirs(settings.BACKUP_DIR, exist_ok=True)
            
            # 获取所有数据
            signals = db.query(TradingSignalModel).all()
            backup_data = [{
                'trade_id': s.trade_id,
                'title': s.title,
                'currentcy': s.currentcy,
                'open_price': s.open_price,
                'close_price': s.close_price,
                'profit_percentage': s.profit_percentage,
                'created_at': s.created_at.isoformat(),
                'closed_at': s.closed_at.isoformat() if s.closed_at else None
            } for s in signals]
            
            # 创建备份文件
            filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(settings.BACKUP_DIR, filename)
            
            with open(filepath, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            # 清理旧备份
            await BackupService.cleanup_old_backups()
            
            logger.info(f"Database backup created: {filename}")
            return filepath
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise

    @staticmethod
    async def cleanup_old_backups():
        try:
            retention_date = datetime.now() - timedelta(days=settings.BACKUP_RETENTION_DAYS)
            
            for filename in os.listdir(settings.BACKUP_DIR):
                if not filename.startswith('backup_'):
                    continue
                    
                filepath = os.path.join(settings.BACKUP_DIR, filename)
                file_date = datetime.strptime(filename[7:15], '%Y%m%d')
                
                if file_date < retention_date:
                    os.remove(filepath)
                    logger.info(f"Removed old backup: {filename}")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}") 