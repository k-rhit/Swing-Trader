"""
Convenience accessors for OHLCV columns.

Using these helpers instead of df["Close"] directly makes strategy code more
readable and provides a single place to adapt if column naming ever changes.
"""

import pandas as pd


class OHLCV:

    @staticmethod
    def open(df: pd.DataFrame) -> pd.Series:
        return df["Open"]

    @staticmethod
    def high(df: pd.DataFrame) -> pd.Series:
        return df["High"]

    @staticmethod
    def low(df: pd.DataFrame) -> pd.Series:
        return df["Low"]

    @staticmethod
    def close(df: pd.DataFrame) -> pd.Series:
        return df["Close"]

    @staticmethod
    def volume(df: pd.DataFrame) -> pd.Series:
        return df["Volume"]