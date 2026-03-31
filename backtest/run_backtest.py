from backtest.engine.backtester import Backtester
from src.strategies.sma_strategy import SMAStrategy
import yfinance as yf

df = yf.download("RELIANCE.NS", period="1y")

bt = Backtester()
result = bt.run(df, SMAStrategy())

print(result)