from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np

class MLService:
    @staticmethod
    async def train_model(historical_data: pd.DataFrame):
        try:
            # 准备训练数据
            X = historical_data[['price', 'volume', 'ma_5', 'ma_10', 'rsi']]
            y = historical_data['profit'] > 0
            
            # 训练模型
            model = RandomForestClassifier(n_estimators=100)
            model.fit(X, y)
            
            # 保存模型
            await MLService.save_model(model)
            
            return model
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise 