import os
import json

class Config:

    @staticmethod
    def tg_token():
        return os.getenv("TELEGRAM_BOT_TOKEN")

    @staticmethod
    def tg_chat_id():
        return os.getenv("TELEGRAM_CHAT_ID")

    @staticmethod
    def load_symbols():
        with open("src/data/symbols_all.json") as f:
            return json.load(f)