import matplotlib.pyplot as plt
import os
from datetime import datetime
import pandas as pd
from ..utils.logger import setup_logger
import matplotlib.font_manager as fm

class ImageService:
    def __init__(self):
        self.logger = setup_logger("image_service")
        # 确保 static/images 目录存在
        self.image_dir = "static/images"
        os.makedirs(self.image_dir, exist_ok=True)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    def generate_strategy_image(self, signals, strategy_name: str) -> str:
        """生成策略图片"""
        try:
            if not signals:
                self.logger.error("No signals provided")
                return ""

            # 创建数据列表
            data = []
            total_profit = 0
            
            # 记录交易序号
            trade_count = 1
            
            for signal in signals:
                if signal.is_close and signal.profit_percentage is not None:
                    profit = float(signal.profit_percentage)
                    total_profit += profit
                    self.logger.debug(f"Processing signal {trade_count}: profit={profit}")
                    
                    data.append([
                        str(trade_count),
                        '多' if signal.side == 'buy' else '空',
                        signal.created_at.strftime('%Y-%m-%d %H:%M'),
                        f"{profit:.2f}%",
                        str(signal.lever),
                        f"{profit:.2f}%"
                    ])
                    trade_count += 1

            if not data:
                self.logger.error("No valid trade data found")
                return ""

            # 创建图表
            fig, ax = plt.subplots(figsize=(12, len(data) * 0.5 + 3))
            ax.axis('tight')
            ax.axis('off')

            # 定义列标题
            columns = ['交易 #', '类型', '日期时间', '获利%', '杠杆倍数', '收益%']

            # 创建表格
            table = ax.table(
                cellText=data,
                colLabels=columns,
                cellLoc='center',
                loc='center',
                cellColours=[['white']*len(columns)]*len(data),
                colColours=['lightgray']*len(columns)
            )

            # 设置标题
            plt.title(f"趋势交易策略90 #{strategy_name}\n", pad=20, fontsize=14)

            # 添加总收益
            plt.figtext(0.1, 0.02, f"{signals[0].created_at.strftime('%m月%d日')}--{signals[-1].created_at.strftime('%m月%d日')} 收益合计: {total_profit:.2f}%", fontsize=10)

            # 调整表格样式
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1.2, 1.8)

            # 为正负收益设置不同颜色
            for i in range(len(data)):
                try:
                    profit = float(data[i][3].strip('%'))  # 使用获利%列
                    color = 'green' if profit > 0 else 'red'
                    for j in [3, 5]:  # 同时设置获利%和收益%列的颜色
                        cell = table.get_celld()[(i+1, j)]
                        cell.set_text_props(color=color)
                except Exception as e:
                    self.logger.error(f"Error setting color for row {i}: {e}")

            # 保存图片
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{strategy_name}_{timestamp}.png"
            filepath = os.path.join(self.image_dir, filename)
            plt.savefig(filepath, bbox_inches='tight', dpi=300)
            plt.close()

            self.logger.info(f"Successfully generated image: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error generating strategy image: {e}")
            self.logger.error(f"Data: {data}")
            if 'plt' in locals():
                plt.close()
            return ""

image_service = ImageService() 