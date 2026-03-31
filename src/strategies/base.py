from abc import ABC, abstractmethod
from src.bot.formatter import Formatter

class BaseStrategy(ABC):

    @abstractmethod
    def name(self): pass

    @abstractmethod
    def generate(self, df, symbol): pass

    def build_signal(self, stock, strategy, buy, target):
        return {
            "id": f"{stock}-{strategy}-{buy}",
            "stock": stock,
            "strategy": strategy,
            "buy": buy,
            "target": target,
            "format": lambda: Formatter.signal(stock, strategy, buy, target)
        }

class StrategyEngine:

    @staticmethod
    def load_all():
        from .sma_strategy import SMAStrategy
        from .knoxville import Knoxville
        from .v20 import V20
        from .rhs import RHS
        from .cwh import CWH
        from .v10 import V10
        from .lifetime_high import LifetimeHigh
        from .three_x_three_years import ThreeX

        return [
            SMAStrategy(),
            Knoxville(),
            V20(),
            RHS(),
            CWH(),
            V10(),
            LifetimeHigh(),
            ThreeX()
        ]