"""
Shared technical indicator calculations.

All functions accept a pd.Series or pd.DataFrame and return a pd.Series.
Kept pure (no side-effects) so they are safe to use in both live and
backtest contexts.

Indicators:
    wilder_rsi      — Wilder-smoothed RSI (industry standard)
    ema             — Exponential Moving Average
    sma             — Simple Moving Average
    atr             — Average True Range (Wilder method)
    bollinger_bands — Upper / middle / lower Bollinger Bands
    macd            — MACD line, signal line, histogram
    adx             — Average Directional Index (trend strength)
"""

from typing import Tuple
import numpy as np
import pandas as pd


# ──────────────────────────────────────────────────────────────────────────────
# RSI
# ──────────────────────────────────────────────────────────────────────────────

def wilder_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """
    Wilder-smoothed Relative Strength Index.

    Args:
        close:  Closing price series.
        period: Look-back window (default 14).

    Returns:
        RSI series in the range [0, 100].
    """
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    return (100 - (100 / (1 + rs))).rename("RSI")


# ──────────────────────────────────────────────────────────────────────────────
# Moving Averages
# ──────────────────────────────────────────────────────────────────────────────

def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=period, adjust=False).mean().rename(f"EMA{period}")


def sma(series: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(period).mean().rename(f"SMA{period}")


# ──────────────────────────────────────────────────────────────────────────────
# ATR (Average True Range)
# ──────────────────────────────────────────────────────────────────────────────

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Wilder Average True Range.

    Args:
        df:     DataFrame with High, Low, Close columns.
        period: Smoothing window (default 14).

    Returns:
        ATR series.
    """
    high = df["High"]
    low = df["Low"]
    prev_close = df["Close"].shift(1)

    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)

    return tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean().rename("ATR")


# ──────────────────────────────────────────────────────────────────────────────
# Bollinger Bands
# ──────────────────────────────────────────────────────────────────────────────

def bollinger_bands(
    close: pd.Series,
    period: int = 20,
    num_std: float = 2.0,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Bollinger Bands.

    Args:
        close:   Closing price series.
        period:  Look-back window (default 20).
        num_std: Number of standard deviations for the bands (default 2.0).

    Returns:
        (upper_band, middle_band, lower_band) as a tuple of pd.Series.
    """
    middle = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = (middle + num_std * std).rename("BB_upper")
    lower = (middle - num_std * std).rename("BB_lower")
    middle = middle.rename("BB_mid")
    return upper, middle, lower


# ──────────────────────────────────────────────────────────────────────────────
# MACD
# ──────────────────────────────────────────────────────────────────────────────

def macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal_period: int = 9,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Moving Average Convergence / Divergence.

    Args:
        close:         Closing price series.
        fast:          Fast EMA period (default 12).
        slow:          Slow EMA period (default 26).
        signal_period: Signal line EMA period (default 9).

    Returns:
        (macd_line, signal_line, histogram) as a tuple of pd.Series.
    """
    fast_ema = close.ewm(span=fast, adjust=False).mean()
    slow_ema = close.ewm(span=slow, adjust=False).mean()
    macd_line = (fast_ema - slow_ema).rename("MACD")
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean().rename("MACD_signal")
    histogram = (macd_line - signal_line).rename("MACD_hist")
    return macd_line, signal_line, histogram


# ──────────────────────────────────────────────────────────────────────────────
# ADX (Average Directional Index)
# ──────────────────────────────────────────────────────────────────────────────

def adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Average Directional Index — measures trend strength (not direction).

    ADX > 25 → strong trend; ADX < 20 → weak / ranging market.

    Args:
        df:     DataFrame with High, Low, Close columns.
        period: Smoothing window (default 14).

    Returns:
        ADX series in the range [0, 100].
    """
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_high = high.shift(1)
    prev_low = low.shift(1)
    prev_close = close.shift(1)

    # True Range
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)

    # Directional movement
    dm_pos = (high - prev_high).clip(lower=0)
    dm_neg = (prev_low - low).clip(lower=0)
    # If both are positive, keep only the larger one; zero the other
    both_pos = (dm_pos > 0) & (dm_neg > 0)
    dm_pos = dm_pos.where(~both_pos | (dm_pos >= dm_neg), 0)
    dm_neg = dm_neg.where(~both_pos | (dm_neg > dm_pos), 0)

    alpha = 1 / period
    atr_s = tr.ewm(alpha=alpha, adjust=False).mean()
    di_pos = 100 * dm_pos.ewm(alpha=alpha, adjust=False).mean() / atr_s
    di_neg = 100 * dm_neg.ewm(alpha=alpha, adjust=False).mean() / atr_s

    dx = (100 * (di_pos - di_neg).abs() / (di_pos + di_neg).replace(0, np.nan))
    return dx.ewm(alpha=alpha, adjust=False).mean().rename("ADX")