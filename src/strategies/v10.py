from src.strategies.base import BaseStrategy
from src.utils.patterns import Patterns

class V10(BaseStrategy):

    def name(self): return "V10"

    def generate(self, df, symbol):
        p = Patterns.detect_v10(df)
        if p and p["valid"]:
            buy = f"{df['Close'].iloc[-1]}"
            target = f"{df['Close'].iloc[-1] * 1.1:.2f}"
            return self.build_signal(symbol, self.name(), buy, target)
        return None