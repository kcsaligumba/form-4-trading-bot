from typing import Dict
from config import MIN_DOLLAR_VALUE, MIN_PCT_ADV, PRIORITY_TITLES

def compute_features(tx: Dict, adv_usd: float | None) -> Dict:
    dv = (tx["shares"] or 0) * (tx["price"] or 0)
    pct_adv = (dv / adv_usd * 100.0) if adv_usd and adv_usd > 0 else None

    score = 0
    if tx.get("transaction_code") == "P": score += 3              # open-market purchase
    if tx.get("is_officer"): score += 2
    title = (tx.get("officer_title") or "").lower()
    if any(k in title for k in PRIORITY_TITLES): score += 1
    if dv >= MIN_DOLLAR_VALUE: score += 2
    if (pct_adv or 0) >= MIN_PCT_ADV: score += 2
    if tx.get("is_10b5_1_plan"): score -= 2

    return {"dollar_value": dv, "pct_adv": pct_adv, "score": score}
