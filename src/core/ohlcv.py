class OHLCV:
    @staticmethod
    def low(df): return df["Low"]
    @staticmethod
    def high(df): return df["High"]
    @staticmethod
    def close(df): return df["Close"]
    @staticmethod
    def open(df): return df["Open"]