import os
from dotenv import load_dotenv

load_dotenv()

SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "your-email@example.com")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
MIN_DOLLAR_VALUE = float(os.getenv("MIN_DOLLAR_VALUE", "250000"))
MIN_PCT_ADV = float(os.getenv("MIN_PCT_ADV", "10"))
PRIORITY_TITLES = tuple(s.strip().lower() for s in os.getenv(
    "PRIORITY_TITLES", "ceo,cfo,chief executive,chief financial"
).split(","))
SCORE_ALERT_THRESHOLD=6