import requests
from src.core.config import Config
from src.utils.logger import logger

class TelegramBot:

    def send_message(self, text):
        url = f"https://api.telegram.org/bot{Config.tg_token()}/sendMessage"
        payload = {"chat_id": Config.tg_chat_id(), "text": text}
        try:
            requests.post(url, data=payload)
        except Exception as e:
            logger.error(f"Telegram error: {e}")