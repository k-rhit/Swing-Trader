from src.strategies.base import BaseStrategy
import numpy as np

class Knoxville(BaseStrategy):

    def name(self): return "Knoxville Divergence"

    def generate(self, df, symbol):
        rsi = df["Close"].pct_change().rolling(14).mean()
        mom = df["Close"].diff(20)

        if rsi.iloc[-1] < 0 and mom.iloc[-1] > 0:
            buy = f"{df['Close'].iloc[-1]}"
            target = "Next Knoxville Uptrend"
            return self.build_signal(symbol, self.name(), buy, target)
        return None