import pandas as pd
import yfinance as yf
from typing import Optional

def get_adv_usd(symbol: str, lookback_days: int = 30) -> Optional[float]:
    try:
        df = yf.download(symbol, period="60d", interval="1d", progress=False, auto_adjust=False)
        if df.empty or "Close" not in df or "Volume" not in df:
            return None
        dv = (df["Close"] * df["Volume"]).tail(lookback_days)
        if dv.empty:
            return None
        mean_dv = dv.mean()
        if hasattr(mean_dv, "iloc"):
            return float(mean_dv.iloc[0])
        return float(mean_dv)
    except Exception:
        return None
