from __future__ import annotations
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .config import get_settings

settings = get_settings()

EST = pytz.timezone("US/Eastern")
IST = pytz.timezone("Asia/Kolkata")

_scheduler: BackgroundScheduler | None = None


def is_us_market_open() -> bool:
    now = datetime.now(EST)
    if now.weekday() >= 5:
        return False
    open_t = now.replace(hour=9, minute=30, second=0, microsecond=0)
    close_t = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return open_t <= now <= close_t


def is_india_market_open() -> bool:
    now = datetime.now(IST)
    if now.weekday() >= 5:
        return False
    open_t = now.replace(hour=9, minute=15, second=0, microsecond=0)
    close_t = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return open_t <= now <= close_t


def is_any_market_open() -> bool:
    return True  # crypto is 24/7; we always run but skip stock-only tickers outside hours


def scheduled_run():
    print(f"\n🕐 Scheduler triggered at {datetime.utcnow().isoformat()}Z")
    print(f"   US market open: {is_us_market_open()}")
    print(f"   India market open: {is_india_market_open()}")

    from .signals.signal_runner import SignalRunner
    runner = SignalRunner()

    # Always run crypto
    crypto_tickers = settings.crypto_watchlist
    for ticker in crypto_tickers:
        runner.run_for_ticker(ticker, "crypto")

    # Run stocks only during market hours
    if is_us_market_open():
        for ticker in settings.us_watchlist:
            runner.run_for_ticker(ticker, "us")
        for ticker in settings.etf_watchlist:
            runner.run_for_ticker(ticker, "etf")

    if is_india_market_open():
        for ticker in settings.india_watchlist:
            runner.run_for_ticker(ticker, "india")

    print("✅ Scheduler run complete\n")


def start_scheduler():
    global _scheduler
    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        scheduled_run,
        trigger=IntervalTrigger(minutes=settings.schedule_interval_min),
        id="trading_signal_job",
        replace_existing=True,
    )
    _scheduler.start()
    print(f"⏰ Scheduler started — running every {settings.schedule_interval_min} min")


def stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        print("⏰ Scheduler stopped")
