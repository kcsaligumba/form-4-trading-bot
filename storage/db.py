from datetime import datetime, timedelta
from sqlalchemy import (create_engine, Column, Integer, String, Float, DateTime,
                        Boolean, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine("sqlite:///data.db", future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class Filing(Base):
    __tablename__ = "filings"
    id = Column(Integer, primary_key=True)
    accession_no = Column(String, unique=True, index=True)
    cik = Column(String, index=True, nullable=True)
    symbol = Column(String, index=True, nullable=True)
    filing_date = Column(String, nullable=True)        # periodOfReport
    accepted_at = Column(DateTime, nullable=True)      # EDGAR acceptance time if known
    documents_url = Column(String, nullable=False)     # “Documents” page
    created_at = Column(DateTime, default=datetime.utcnow)
    transactions = relationship("Transaction", back_populates="filing")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    filing_id = Column(Integer, ForeignKey("filings.id"))
    transaction_code = Column(String)
    transaction_date = Column(String)
    shares = Column(Float)
    price = Column(Float)
    dollar_value = Column(Float)
    owner_name = Column(String)
    is_officer = Column(Boolean, default=False)
    is_director = Column(Boolean, default=False)
    officer_title = Column(String)
    shares_after = Column(Float, nullable=True)
    is_10b5_1_plan = Column(Boolean, default=False)
    pct_adv = Column(Float, nullable=True)
    score = Column(Integer, default=0)
    filing = relationship("Filing", back_populates="transactions")

class Watchlist(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    __table_args__ = (UniqueConstraint("symbol", name="uq_watchlist_symbol"),)

def add_to_watchlist(db, symbol: str, days: int = 10):
    from sqlalchemy.exc import IntegrityError
    now = datetime.utcnow()
    expiry = now + timedelta(days=days)
    w = Watchlist(symbol=symbol, added_at=now, expires_at=expiry)
    db.add(w)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()

def cleanup_watchlist(db):
    now = datetime.utcnow()
    db.query(Watchlist).filter(Watchlist.expires_at < now).delete()
    db.commit()

def init_db():
    Base.metadata.create_all(engine)
