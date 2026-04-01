"""
Base strategy contract and strategy loader.

All strategies inherit from BaseStrategy and must implement:
    name()     → human-readable strategy name
    generate() → returns a signal dict or None

Signal dicts are plain JSON-serialisable objects EXCEPT for the "format_fn"
key which holds a callable.  SignalManager strips "format_fn" before saving.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from src.bot.formatter import Formatter


class BaseStrategy(ABC):

    @abstractmethod
    def name(self) -> str:
        """Return a short, unique strategy identifier."""

    @abstractmethod
    def generate(self, df, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Analyse *df* for *symbol* and return a signal dict or None.

        The returned dict must include at minimum:
            id, stock, strategy, buy, target
        Plus a non-serialisable "format_fn" callable for Telegram formatting.
        """

    def build_signal(
        self,
        stock: str,
        strategy: str,
        buy: str,
        target: str,
        stoploss: str = "—",
    ) -> Dict[str, Any]:
        """
        Construct a standardised signal dict.

        The "id" field deduplicates signals: one signal per stock+strategy
        combination per day (buy price is part of the key so the same stock
        can appear under different strategies).

        Args:
            stock:    NSE ticker, e.g. "RELIANCE".
            strategy: Strategy name string.
            buy:      Buy range as a formatted string, e.g. "₹2450 – ₹2470".
            target:   Target price as a string.
            stoploss: Optional stoploss string.

        Returns:
            Signal dict ready for SignalManager.
        """
        sig = {
            "id": f"{stock}-{strategy}-{buy}",
            "stock": stock,
            "strategy": strategy,
            "buy": buy,
            "target": target,
            "stoploss": stoploss,
            # format_fn is a callable — stripped by SignalManager before JSON save
            "format_fn": lambda s=None: Formatter.signal(
                {"stock": stock, "strategy": strategy, "buy": buy,
                 "target": target, "stoploss": stoploss}
            ),
        }
        return sig


class StrategyEngine:
    """Discovers and instantiates all available strategies."""

    @staticmethod
    def load_all() -> list:
        # Local imports avoid circular dependencies at module load time.
        from src.strategies.sma_strategy import SMAStrategy
        from src.strategies.knoxville import Knoxville
        from src.strategies.v20 import V20
        from src.strategies.rhs import RHS
        from src.strategies.cwh import CWH
        from src.strategies.v10 import V10
        from src.strategies.lifetime_high import LifetimeHigh
        from src.strategies.three_x_three_years import ThreeX

        return [
            SMAStrategy(),
            Knoxville(),
            V20(),
            RHS(),
            CWH(),
            V10(),
            LifetimeHigh(),
            ThreeX(),
        ]