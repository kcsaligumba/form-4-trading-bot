import time
import os
import argparse
from datetime import datetime
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.exc import IntegrityError

from config import POLL_INTERVAL_SECONDS, SCORE_ALERT_THRESHOLD
from storage.db import init_db, SessionLocal, Filing, Transaction, add_to_watchlist, cleanup_watchlist
from ingest.discover import get_current_form4_entries
from ingest.fetch import find_ownership_xml_url, fetch_ownership_xml
from ingest.parse import parse_ownership_xml
from market.prices import get_adv_usd
from features.engineer import compute_features
from alerts.discord import send_discord_alert

def process_once(alert_all: bool = False):
    db = SessionLocal()
    try:
        cleanup_watchlist(db)

        entries = get_current_form4_entries(limit=60)
        logger.info(f"Discovered {len(entries)} recent Form-4 entries")
        for e in entries:
            # Dedup by accession_no
            if db.query(Filing).filter(Filing.accession_no == e["accession_no"]).first():
                continue

            # Find ownership.xml
            xml_url = find_ownership_xml_url(e["dir_url"])
            if not xml_url:
                continue

            xml_bytes = fetch_ownership_xml(xml_url)
            parsed = parse_ownership_xml(xml_bytes)
            symbol = parsed["symbol"]
            if not symbol:
                continue

            filing = Filing(
                accession_no=e["accession_no"],
                cik=parsed["cik"],
                symbol=symbol,
                filing_date=parsed["filing_date"],
                accepted_at=None,            # could be improved if you capture acceptance time from index source
                documents_url=e["documents_url"]
            )
            db.add(filing)
            try:
                db.commit()
                db.refresh(filing)
            except IntegrityError:
                db.rollback()
                continue

            adv = get_adv_usd(symbol)

            for tx in parsed["transactions"]:
                feats = compute_features(tx, adv)
                rec = Transaction(
                    filing_id=filing.id,
                    transaction_code=tx["transaction_code"],
                    transaction_date=tx["transaction_date"],
                    shares=tx["shares"],
                    price=tx["price"],
                    dollar_value=feats["dollar_value"],
                    owner_name=tx["owner_name"],
                    is_officer=tx["is_officer"],
                    is_director=tx["is_director"],
                    officer_title=tx["officer_title"],
                    shares_after=tx["shares_after"],
                    is_10b5_1_plan=tx["is_10b5_1_plan"],
                    pct_adv=feats["pct_adv"],
                    score=feats["score"]
                )
                db.add(rec)
                db.commit()

                # Alert & watchlist
                should_alert = alert_all or (rec.score >= SCORE_ALERT_THRESHOLD and rec.transaction_code == "P")
                if should_alert:
                    send_discord_alert({
                        "symbol": symbol,
                        "transaction_code": rec.transaction_code,
                        "dollar_value": rec.dollar_value or 0.0,
                        "pct_adv": rec.pct_adv,
                        "is_officer": rec.is_officer,
                        "officer_title": rec.officer_title,
                        "is_10b5_1_plan": rec.is_10b5_1_plan,
                        "documents_url": filing.documents_url,
                        "score": rec.score
                    })
                    if not alert_all and rec.transaction_code == "P":
                        add_to_watchlist(db, symbol, days=10)

    finally:
        db.close()

def main(alert_all: bool = False):
    init_db()
    logger.info("Starting SEC Form-4 bot…")
    process_once(alert_all=alert_all)  # run immediately
    sched = BackgroundScheduler(timezone="UTC")
    sched.add_job(process_once, "interval", seconds=POLL_INTERVAL_SECONDS, max_instances=1, coalesce=True, kwargs={"alert_all": alert_all})
    sched.start()
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        logger.info("Shutting down…")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SEC Form-4 Bot")
    parser.add_argument(
        "--test-alert",
        action="store_true",
        help="Send a simulated high-priority insider trade alert to Discord and exit."
    )
    parser.add_argument(
        "--reset-db",
        action="store_true",
        help="Delete data.db before starting (forces reprocessing)."
    )
    parser.add_argument(
        "--alert-all",
        action="store_true",
        help="Send Discord alerts for every parsed transaction (debugging)."
    )
    args = parser.parse_args()

    if args.test_alert:
        from alerts.discord import send_discord_alert

        fake_event = {
            "symbol": "AAPL",
            "transaction_code": "P",
            "dollar_value": 500000,
            "pct_adv": 25.5,
            "is_officer": True,
            "officer_title": "Chief Executive Officer",
            "is_10b5_1_plan": False,
            "documents_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/0000320193-24-000123-index.htm",
            "score": 8
        }

        send_discord_alert(fake_event)
        print("✅ Test alert sent! Check your Discord channel.")
        exit(0)

    if args.reset_db:
        db_path = os.path.join(os.getcwd(), "data.db")
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info("Deleted data.db for a fresh run.")
        else:
            logger.info("data.db not found; starting fresh.")

    # Normal run
    main(alert_all=args.alert_all)
