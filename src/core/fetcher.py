"""
Market data fetcher using yfinance.

yfinance ≥ 0.2 returns a MultiIndex column DataFrame when downloading a single
ticker with group_by="column" (the new default).  We normalise the output to a
flat-column DataFrame with standard OHLCV names so all downstream code is
insulated from the yfinance API change.
"""

from typing import Optional
import pandas as pd
import yfinance as yf

from src.utils.logger import logger


class DataFetcher:

    def get(self, symbol: str, period: str = "3y") -> Optional[pd.DataFrame]:
        """
        Download daily OHLCV data for *symbol* (NSE ticker, without .NS suffix).

        Args:
            symbol: NSE symbol, e.g. "RELIANCE".
            period:  yfinance period string, e.g. "1y", "3y".

        Returns:
            Flat DataFrame with columns [Open, High, Low, Close, Volume] and a
            DatetimeIndex, or None on failure.
        """
        ticker = symbol + ".NS"
        try:
            df = yf.download(
                ticker,
                period=period,
                interval="1d",
                progress=False,
                auto_adjust=True,   # adjusts for splits/dividends automatically
            )
        except Exception as exc:
            logger.error(f"Network error fetching {ticker}: {exc}")
            return None

        if df is None or df.empty:
            logger.warning(f"No data returned for {ticker}")
            return None

        # ------------------------------------------------------------------
        # yfinance ≥ 0.2 returns a MultiIndex like (field, ticker).
        # Flatten to simple column names.
        # ------------------------------------------------------------------
        if isinstance(df.columns, pd.MultiIndex):
            # Keep only the first level (field names) — there is only one ticker
            df.columns = df.columns.get_level_values(0)

        # Keep only the columns we care about; drop "Dividends", "Stock Splits" etc.
        needed = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
        df = df[needed].copy()

        # Drop rows where Close is NaN (e.g. future-dated rows yfinance sometimes adds)
        df.dropna(subset=["Close"], inplace=True)

        if df.empty:
            logger.warning(f"All rows dropped after cleaning for {ticker}")
            return None

        logger.debug(f"Fetched {len(df)} rows for {ticker}")
        return df