import aiohttp
from ..config import settings
from ..utils.logger import setup_logger

class TelegramService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.logger = setup_logger("telegram")
        
    async def send_message(self, message: str):
        """发送消息到 Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={
                    'chat_id': self.chat_id,
                    'text': message
                }) as response:
                    if response.status == 200:
                        self.logger.info("Message sent successfully to Telegram")
                    else:
                        self.logger.error(f"Failed to send message: {await response.text()}")
        except Exception as e:
            self.logger.error(f"Error sending message to Telegram: {e}")

telegram_service = TelegramService() 