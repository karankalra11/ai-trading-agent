import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from .base_market import BaseMarketFetcher
from ..config import get_settings

settings = get_settings()
IST = pytz.timezone("Asia/Kolkata")


class IndiaStockFetcher(BaseMarketFetcher):

    def get_watchlist(self) -> list[str]:
        return settings.india_watchlist

    def get_exchange(self) -> str:
        return "NSE/BSE"

    def get_asset_type(self) -> str:
        return "stock"

    def is_market_open(self) -> bool:
        now = datetime.now(IST)
        if now.weekday() >= 5:  # Saturday/Sunday
            return False
        open_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
        close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
        return open_time <= now <= close_time

    def normalize_ticker(self, ticker: str) -> str:
        """Ensure ticker has .NS suffix for yfinance."""
        if not ticker.endswith((".NS", ".BO")):
            return ticker + ".NS"
        return ticker

    def fetch_ohlcv(self, ticker: str, period: str = "5d", interval: str = "30m") -> pd.DataFrame:
        try:
            norm = self.normalize_ticker(ticker)
            df = yf.download(norm, period=period, interval=interval, progress=False, auto_adjust=True)
            if df.empty:
                return pd.DataFrame()
            df.columns = [c.lower() if isinstance(c, str) else c[0].lower() for c in df.columns]
            df = df[["open", "high", "low", "close", "volume"]].dropna()
            return df
        except Exception as e:
            print(f"⚠️  India OHLCV fetch failed for {ticker}: {e}")
            return pd.DataFrame()

    def fetch_current_price(self, ticker: str) -> dict:
        try:
            norm = self.normalize_ticker(ticker)
            t = yf.Ticker(norm)
            info = t.fast_info
            hist = t.history(period="2d", interval="1d", auto_adjust=True)
            pct_change = 0.0
            if len(hist) >= 2:
                pct_change = round((hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2] * 100, 2)
            return {
                "ticker": ticker,
                "price": round(float(info.last_price or 0), 4),
                "volume": float(info.three_month_average_volume or 0),
                "market_cap": float(info.market_cap or 0),
                "pct_change_24h": pct_change,
                "high_52w": round(float(info.year_high or 0), 4),
                "low_52w": round(float(info.year_low or 0), 4),
            }
        except Exception as e:
            print(f"⚠️  India price fetch failed for {ticker}: {e}")
            return {"ticker": ticker, "price": 0, "volume": 0, "market_cap": 0,
                    "pct_change_24h": 0, "high_52w": 0, "low_52w": 0}
