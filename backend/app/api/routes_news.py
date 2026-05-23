from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..database import get_db
from ..models import NewsSentiment

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/{ticker}")
def get_news(
    ticker: str,
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = (
        db.query(NewsSentiment)
        .filter(NewsSentiment.ticker == ticker.upper())
        .order_by(desc(NewsSentiment.fetched_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "id": n.id,
            "ticker": n.ticker,
            "headline": n.headline,
            "source": n.source,
            "url": n.url,
            "published_at": n.published_at.isoformat() if n.published_at else None,
            "sentiment_label": n.sentiment_label,
            "sentiment_score": n.sentiment_score,
            "source_type": n.source_type,
            "fetched_at": n.fetched_at.isoformat() if n.fetched_at else None,
        }
        for n in items
    ]


@router.get("/{ticker}/sentiment-history")
def get_sentiment_history(
    ticker: str,
    limit: int = Query(48, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Returns time-series sentiment for the sentiment timeline chart."""
    from ..models import Signal
    signals = (
        db.query(Signal)
        .filter(Signal.ticker == ticker.upper())
        .order_by(desc(Signal.created_at))
        .limit(limit)
        .all()
    )
    # Derive sentiment from confidence + signal direction as a proxy
    history = []
    for s in reversed(signals):
        direction = 1 if s.signal == "BUY" else -1 if s.signal == "SELL" else 0
        score = direction * ((s.confidence or 50) / 100)
        history.append({
            "timestamp": s.created_at.isoformat() if s.created_at else None,
            "score": round(score, 4),
            "signal": s.signal,
            "confidence": s.confidence,
        })
    return history
