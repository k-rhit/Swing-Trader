from src.strategies.base import BaseStrategy

class LifetimeHigh(BaseStrategy):

    def name(self): return "Lifetime High Strategy"

    def generate(self, df, symbol):
        high = df["High"].max()
        c = df["Close"].iloc[-1]

        if c < high * 0.70:
            buy = f"{c}"
            target = f"{high}"
            return self.build_signal(symbol, self.name(), buy, target)
        return None