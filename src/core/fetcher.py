import yfinance as yf
from src.utils.logger import logger

class DataFetcher:

    def get(self, symbol, period="1y"):
        try:
            df = yf.download(symbol+".NS", period=period, interval="1d", progress=False)
            return df
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None