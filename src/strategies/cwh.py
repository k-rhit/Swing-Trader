from src.strategies.base import BaseStrategy
from src.utils.patterns import Patterns

class CWH(BaseStrategy):

    def name(self): return "Cup With Handle"

    def generate(self, df, symbol):
        p = Patterns.detect_cwh(df)
        if p and p["valid"]:
            buy = f"{df['Close'].iloc[-1]}"
            target = f"{df['Close'].iloc[-1] * 1.35:.2f}"
            return self.build_signal(symbol, self.name(), buy, target)
        return None