import httpx
from config import DISCORD_WEBHOOK_URL, SEC_USER_AGENT

def send_discord_alert(payload: dict):
    if not DISCORD_WEBHOOK_URL:
        return
    content = (
        f"**Insider Signal** {payload.get('symbol')}\n"
        f"- Code: {payload.get('transaction_code')}  "
        f"- ${payload.get('dollar_value'):,.0f}  "
        f"- %ADV: {payload.get('pct_adv') and round(payload['pct_adv'],1)}\n"
        f"- Officer: {payload.get('is_officer')}  "
        f"- Title: {payload.get('officer_title') or '—'}  "
        f"- Plan10b5-1: {payload.get('is_10b5_1_plan')}\n"
        f"- Link: {payload.get('documents_url')}\n"
        f"- Score: **{payload.get('score')}**"
    )
    httpx.post(DISCORD_WEBHOOK_URL, json={"content": content}, headers={"User-Agent": SEC_USER_AGENT}, timeout=20)
