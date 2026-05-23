import yfinance as yf
import pandas as pd
from .base_market import BaseMarketFetcher
from ..config import get_settings

settings = get_settings()


class USStockFetcher(BaseMarketFetcher):

    def get_watchlist(self) -> list[str]:
        return settings.us_watchlist

    def get_exchange(self) -> str:
        return "NASDAQ/NYSE"

    def get_asset_type(self) -> str:
        return "stock"

    def fetch_ohlcv(self, ticker: str, period: str = "5d", interval: str = "30m") -> pd.DataFrame:
        try:
            df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
            if df.empty:
                return pd.DataFrame()
            df.columns = [c.lower() if isinstance(c, str) else c[0].lower() for c in df.columns]
            df = df[["open", "high", "low", "close", "volume"]].dropna()
            return df
        except Exception as e:
            print(f"⚠️  US OHLCV fetch failed for {ticker}: {e}")
            return pd.DataFrame()

    def fetch_current_price(self, ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
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
            print(f"⚠️  US price fetch failed for {ticker}: {e}")
            return {"ticker": ticker, "price": 0, "volume": 0, "market_cap": 0,
                    "pct_change_24h": 0, "high_52w": 0, "low_52w": 0}
