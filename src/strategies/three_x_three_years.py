from src.strategies.base import BaseStrategy

class ThreeX(BaseStrategy):

    def name(self): return "3X in 3 Years"

    def generate(self, df, symbol):
        high = df["High"].max()
        c = df["Close"].iloc[-1]

        if c < high * 0.33:
            buy = f"{c}"
            target = f"{high}"
            return self.build_signal(symbol, self.name(), buy, target)
        return None