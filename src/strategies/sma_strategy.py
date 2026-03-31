from src.strategies.base import BaseStrategy
import pandas as pd

class SMAStrategy(BaseStrategy):

    def name(self): return "SMA-20-50-200"

    def generate(self, df, symbol):
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        df["SMA200"] = df["Close"].rolling(200).mean()

        c = df.iloc[-1]
        cond = (
            c.SMA200 > c.SMA50 > c.SMA20 and
            c.Close == df["Low"].iloc[-1]
        )
        if cond:
            buy = f"{c.Close} - {c.Close * 1.01:.2f}"
            target = "Dynamic (Exit when MA reversal)"
            return self.build_signal(symbol, self.name(), buy, target)
        return None