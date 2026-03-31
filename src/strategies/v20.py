from src.strategies.base import BaseStrategy

class V20(BaseStrategy):

    def name(self): return "V20"

    def generate(self, df, symbol):
        recent = df.tail(5)
        if all(recent["Close"].pct_change().fillna(0) > 0):
            if recent["Close"].iloc[-1] > recent["Close"].iloc[0] * 1.20:
                buy = f"{recent['Close'].iloc[-1]}"
                target = "Upper V20 Range"
                return self.build_signal(symbol, self.name(), buy, target)
        return None