from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from ..database import get_db
from ..models import Signal

router = APIRouter(prefix="/api/signals", tags=["signals"])


def signal_to_dict(s: Signal) -> dict:
    return {
        "id": s.id,
        "ticker": s.ticker,
        "exchange": s.exchange,
        "asset_type": s.asset_type,
        "signal": s.signal,
        "entry_price": s.entry_price,
        "target_price": s.target_price,
        "stop_loss": s.stop_loss,
        "confidence": s.confidence,
        "reasoning": s.reasoning,
        "timeframe": s.timeframe,
        "data_sources": s.data_sources,
        "risk_reward_ratio": s.risk_reward_ratio,
        "key_risks": s.key_risks,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


# ── Fixed routes MUST come before /{ticker} wildcard ─────────────────────────

@router.get("")
def get_signals(
    exchange: Optional[str] = None,
    asset_type: Optional[str] = None,
    signal_type: Optional[str] = None,
    min_confidence: Optional[float] = Query(None, ge=0, le=100),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Get latest signal per ticker, with optional filters."""
    q = db.query(Signal).order_by(desc(Signal.created_at))
    if exchange:
        q = q.filter(Signal.exchange.ilike(f"%{exchange}%"))
    if asset_type:
        q = q.filter(Signal.asset_type == asset_type)
    if signal_type:
        q = q.filter(Signal.signal == signal_type.upper())
    if min_confidence is not None:
        q = q.filter(Signal.confidence >= min_confidence)

    all_signals = q.limit(500).all()

    # Deduplicate: latest per ticker
    seen = {}
    for s in all_signals:
        if s.ticker not in seen:
            seen[s.ticker] = s

    result = sorted(seen.values(), key=lambda x: x.created_at, reverse=True)
    return [signal_to_dict(s) for s in result[:limit]]


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Aggregated signal statistics."""
    total = db.query(Signal).count()
    buy = db.query(Signal).filter(Signal.signal == "BUY").count()
    sell = db.query(Signal).filter(Signal.signal == "SELL").count()
    hold = db.query(Signal).filter(Signal.signal == "HOLD").count()
    return {"total": total, "buy": buy, "sell": sell, "hold": hold}


@router.get("/run-all")
def run_all_signals(background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Browser-friendly GET — triggers signal generation for ALL tickers.
    Crypto always runs; stocks only during market hours.
    Check results at /api/signals within 2-3 minutes.
    """
    def run():
        from ..scheduler import scheduled_run
        scheduled_run()

    background_tasks.add_task(run)
    return {
        "message": "Signal run started for all tickers.",
        "check_results_at": "/api/signals",
        "note": "Crypto signals generate immediately (24/7). Stock signals only during market hours."
    }


@router.post("/trigger")
def trigger_signal(
    ticker: str,
    market: str = "us",
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Manually trigger a signal run for a single ticker."""
    def run():
        from ..signals.signal_runner import SignalRunner
        runner = SignalRunner()
        runner.run_for_ticker(ticker.upper(), market.lower())

    background_tasks.add_task(run)
    return {"message": f"Signal run triggered for {ticker.upper()} ({market})"}


# ── Wildcard /{ticker} routes LAST ────────────────────────────────────────────

@router.get("/{ticker}/latest")
def get_latest_signal(ticker: str, db: Session = Depends(get_db)):
    s = (
        db.query(Signal)
        .filter(Signal.ticker == ticker.upper())
        .order_by(desc(Signal.created_at))
        .first()
    )
    if not s:
        raise HTTPException(status_code=404, detail=f"No signals found for {ticker}")
    return signal_to_dict(s)


@router.get("/{ticker}")
def get_ticker_signals(
    ticker: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    signals = (
        db.query(Signal)
        .filter(Signal.ticker == ticker.upper())
        .order_by(desc(Signal.created_at))
        .limit(limit)
        .all()
    )
    return [signal_to_dict(s) for s in signals]
