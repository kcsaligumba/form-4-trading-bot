import pandas as pd
import yfinance as yf
from typing import Optional, List

def _candidate_symbols(symbol: str) -> List[str]:
    candidates = [symbol]
    if "/" in symbol:
        parts = [s for s in symbol.split("/") if s]
        candidates.append(symbol.replace("/", "-"))
        candidates.extend(parts)
        for part in parts:
            if len(part) > 1 and part[-1].isalpha() and part[-2] != "-":
                candidates.append(f"{part[:-1]}-{part[-1]}")
    # Preserve order while removing duplicates.
    seen = set()
    ordered = []
    for s in candidates:
        if s not in seen:
            seen.add(s)
            ordered.append(s)
    return ordered

def get_adv_usd(symbol: str, lookback_days: int = 30) -> Optional[float]:
    try:
        if not symbol or symbol.strip().upper() in {"NONE", "N/A"}:
            return None
        for candidate in _candidate_symbols(symbol):
            df = yf.download(candidate, period="60d", interval="1d", progress=False, auto_adjust=False)
            if df.empty or "Close" not in df or "Volume" not in df:
                continue
            dv = (df["Close"] * df["Volume"]).tail(lookback_days)
            if dv.empty:
                continue
            mean_dv = dv.mean()
            if hasattr(mean_dv, "iloc"):
                return float(mean_dv.iloc[0])
            return float(mean_dv)
        return None
    except Exception:
        return None
