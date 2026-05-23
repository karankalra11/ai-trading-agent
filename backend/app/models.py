from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Float, String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    exchange: Mapped[str] = mapped_column(String(20))
    asset_type: Mapped[str] = mapped_column(String(20))  # stock | crypto | etf

    signal: Mapped[str] = mapped_column(String(10))  # BUY | SELL | HOLD
    entry_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    stop_loss: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timeframe: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    data_sources: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    risk_reward_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    key_risks: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    raw_claude_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    open: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    high: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    low: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    close: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    rsi_14: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    macd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    macd_signal: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bb_upper: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bb_lower: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ema_20: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ema_50: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class NewsSentiment(Base):
    __tablename__ = "news_sentiment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    headline: Mapped[str] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
