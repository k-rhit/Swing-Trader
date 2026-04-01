"""
Miscellaneous utility helpers shared across the codebase.

Functions here are pure and stateless — safe to call from strategies,
backtest engine, or scripts without side effects.
"""

from typing import Optional
import pandas as pd


def pct_from_high(df: pd.DataFrame) -> float:
    """
    Return how far the latest close is below the all-time high (in the df window).

    Returns:
        Float in [0, 1].  e.g. 0.30 means price is 30 % below the ATH.
    """
    ath = float(df["High"].max())
    close = float(df["Close"].iloc[-1])
    if ath == 0:
        return 0.0
    return max(0.0, (ath - close) / ath)


def is_trending_up(df: pd.DataFrame, sma_period: int = 50) -> bool:
    """
    Simple trend filter: price is above its *sma_period*-day SMA and
    the SMA itself is rising (today's SMA > yesterday's SMA).

    Args:
        df:         OHLCV DataFrame.
        sma_period: Look-back period for the SMA filter.

    Returns:
        True if in an uptrend.
    """
    if len(df) < sma_period + 1:
        return False
    ma = df["Close"].rolling(sma_period).mean()
    return float(df["Close"].iloc[-1]) > float(ma.iloc[-1]) > float(ma.iloc[-2])


def recent_volume_surge(df: pd.DataFrame, lookback: int = 20, threshold: float = 1.5) -> bool:
    """
    Return True if today's volume is at least *threshold* times the
    *lookback*-day average volume.

    Useful as an additional confirmation filter in breakout strategies.
    """
    if "Volume" not in df.columns or len(df) < lookback + 1:
        return False
    avg_vol = float(df["Volume"].iloc[-(lookback + 1):-1].mean())
    today_vol = float(df["Volume"].iloc[-1])
    if avg_vol == 0:
        return False
    return today_vol >= avg_vol * threshold


def nearest_support(df: pd.DataFrame, lookback: int = 20) -> float:
    """
    Return the lowest low of the last *lookback* bars as a proxy for
    the nearest support level.
    """
    return float(df["Low"].iloc[-lookback:].min())


def format_price(price: float, currency: str = "₹") -> str:
    """Format a price as a currency string with 2 decimal places."""
    return f"{currency}{price:,.2f}"


def safe_last(series: pd.Series) -> Optional[float]:
    """Return the last non-NaN value of a Series, or None if all NaN."""
    valid = series.dropna()
    return float(valid.iloc[-1]) if not valid.empty else None