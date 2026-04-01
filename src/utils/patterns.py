"""
Chart-pattern detectors used by RHS, CWH, and V10 strategies.

Each detector returns a dict with at least {"valid": bool} on success, or None
if the pattern is not present.  All logic operates on a DataFrame that already
has "High", "Low", "Close" columns with a DatetimeIndex.
"""

from typing import Optional, Dict
import numpy as np
import pandas as pd


class Patterns:

    # ------------------------------------------------------------------
    # Reverse Head & Shoulders (RHS)
    # ------------------------------------------------------------------
    @staticmethod
    def detect_rhs(df: pd.DataFrame) -> Optional[Dict]:
        """
        Simplified RHS detector.

        Looks for three consecutive local troughs where the middle trough
        (head) is lower than the two outer troughs (shoulders), and the
        neckline is the average of the two shoulder peaks.

        Requires at least 60 bars of data.
        """
        if len(df) < 60:
            return None

        lows = df["Low"].values
        highs = df["High"].values

        # Use last 60 bars only so the pattern is recent
        window_low = lows[-60:]
        window_high = highs[-60:]

        # Find three distinct troughs (local minima) using a simple scan
        troughs = []
        for i in range(5, len(window_low) - 5):
            if window_low[i] == min(window_low[i - 5 : i + 6]):
                troughs.append((i, window_low[i]))

        if len(troughs) < 3:
            return None

        # Take the three most-spaced troughs
        left, mid, right = troughs[0], troughs[len(troughs) // 2], troughs[-1]

        # Head must be the deepest trough
        if not (mid[1] < left[1] and mid[1] < right[1]):
            return None

        # Shoulders should be at similar price levels (within 10 %)
        if abs(left[1] - right[1]) / max(left[1], right[1]) > 0.10:
            return None

        # Neckline = average of peaks between left-mid and mid-right
        neckline = (
            max(window_high[left[0] : mid[0]]) + max(window_high[mid[0] : right[0]])
        ) / 2

        # Pattern is only actionable if the current close has crossed the neckline
        current_close = df["Close"].iloc[-1]
        if current_close < neckline:
            return None

        return {"valid": True, "neckline": neckline}

    # ------------------------------------------------------------------
    # Cup With Handle (CWH)
    # ------------------------------------------------------------------
    @staticmethod
    def detect_cwh(df: pd.DataFrame) -> Optional[Dict]:
        """
        Simplified Cup-with-Handle detector.

        The cup is identified by a U-shaped price curve over the last 40 bars:
          - price declines in the first third
          - reaches a trough in the middle third
          - recovers in the final third
        The handle is a small consolidation (< 15 % pullback) in the last 10 bars.

        Requires at least 50 bars of data.
        """
        if len(df) < 50:
            return None

        close = df["Close"].values[-50:]
        n = len(close)
        third = n // 3

        left_top = max(close[:third])
        cup_bottom = min(close[third : 2 * third])
        right_top = max(close[2 * third :])

        # Cup depth: bottom should be at least 10 % below the left top
        if cup_bottom >= left_top * 0.90:
            return None

        # Right side should recover to within 10 % of left top
        if right_top < left_top * 0.90:
            return None

        # Handle: last 10 bars should show a shallow pullback (< 15 %)
        handle = close[-10:]
        handle_high = max(handle)
        handle_low = min(handle)
        if (handle_high - handle_low) / handle_high > 0.15:
            return None

        # Breakout: current close should be near / above the right top
        if close[-1] < right_top * 0.98:
            return None

        return {"valid": True, "cup_bottom": cup_bottom, "right_top": right_top}

    # ------------------------------------------------------------------
    # V10 (Sharp V-shaped reversal ≥ 10 %)
    # ------------------------------------------------------------------
    @staticmethod
    def detect_v10(df: pd.DataFrame) -> Optional[Dict]:
        """
        V10 detector.

        Detects a sharp intra-period decline of at least 10 % followed by a
        full recovery.  Uses the last 20 bars.

        Conditions:
          1. A trough exists where the minimum close is ≥ 10 % below the
             period's starting close.
          2. The current (last) close has recovered above the starting close.
        """
        if len(df) < 20:
            return None

        recent = df["Close"].values[-20:]
        start = recent[0]
        trough = min(recent)
        current = recent[-1]

        # Minimum 10 % drawdown
        if trough >= start * 0.90:
            return None

        # Must have recovered above the starting price
        if current < start:
            return None

        drop_pct = (start - trough) / start * 100
        return {"valid": True, "drop_pct": round(drop_pct, 2)}