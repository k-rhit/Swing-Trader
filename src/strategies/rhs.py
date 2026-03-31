from src.strategies.base import BaseStrategy
from src.utils.patterns import Patterns

class RHS(BaseStrategy):

    def name(self): return "Reverse Head & Shoulder"

    def generate(self, df, symbol):
        p = Patterns.detect_rhs(df)
        if p and p["valid"]:
            buy = f"{df['Close'].iloc[-1]}"
            target = f"{p['neckline'] * 1.4:.2f}"
            return self.build_signal(symbol, self.name(), buy, target)
        return None