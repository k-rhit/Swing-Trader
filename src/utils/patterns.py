import numpy as np

class Patterns:

    @staticmethod
    def detect_rhs(df):
        # simplified: detect inverse head and shoulders using local minima
        lows = df["Low"].values
        idx = np.argmin(lows)
        return {"valid": True, "neckline": df["Close"].iloc[-1]} if idx > 10 else None

    @staticmethod
    def detect_cwh(df):
        # simplified: check cup shape using curvature
        close = df["Close"].values
        mid = len(close) // 2
        if close[mid] < close[0] and close[mid] < close[-1]:
            return {"valid": True}
        return None

    @staticmethod
    def detect_v10(df):
        # detect sharp V fall and bounce
        close = df["Close"].pct_change()
        if close.min() < -0.10:
            return {"valid": True}
        return None