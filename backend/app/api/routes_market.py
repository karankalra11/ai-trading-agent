from fastapi import APIRouter, HTTPException, Query
from ..config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/watchlist")
def get_watchlist():
    """All tracked tickers grouped by market."""
    return {
        "us": settings.us_watchlist,
        "india": settings.india_watchlist,
        "crypto": settings.crypto_watchlist,
        "etf": settings.etf_watchlist,
    }


@router.get("/{ticker}/ohlcv")
def get_ohlcv(
    ticker: str,
    period: str = Query("5d", description="e.g. 1d, 5d, 1mo"),
    interval: str = Query("30m", description="e.g. 5m, 30m, 1h, 1d"),
):
    """Return OHLCV bars for candlestick charts."""
    from ..data.us_stocks import USStockFetcher
    from ..data.india_stocks import IndiaStockFetcher
    from ..data.crypto import CryptoFetcher

    ticker_upper = ticker.upper()

    # Determine fetcher
    if ticker_upper in settings.crypto_watchlist or ticker_upper in settings.crypto_id_map:
        fetcher = CryptoFetcher()
    elif ticker_upper.endswith((".NS", ".BO")) or ticker_upper.replace(".NS", "") in [
        t.replace(".NS", "") for t in settings.india_watchlist
    ]:
        fetcher = IndiaStockFetcher()
    else:
        fetcher = USStockFetcher()

    df = fetcher.fetch_ohlcv(ticker_upper, period=period, interval=interval)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No OHLCV data for {ticker}")

    bars = []
    for ts, row in df.iterrows():
        bars.append({
            "time": int(ts.timestamp()) if hasattr(ts, "timestamp") else str(ts),
            "open": round(float(row.get("open") or 0), 4),
            "high": round(float(row.get("high") or 0), 4),
            "low": round(float(row.get("low") or 0), 4),
            "close": round(float(row.get("close") or 0), 4),
            "volume": int(row.get("volume") or 0),
        })
    return bars


@router.get("/{ticker}/indicators")
def get_indicators(ticker: str):
    """Return current technical indicator values for a ticker."""
    from ..data.us_stocks import USStockFetcher
    from ..indicators.technical import TechnicalAnalyzer

    fetcher = USStockFetcher()
    df = fetcher.fetch_ohlcv(ticker.upper())
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data for {ticker}")

    analyzer = TechnicalAnalyzer()
    indicators = analyzer.compute_all(df)
    return indicators
