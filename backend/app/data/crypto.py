import requests
import pandas as pd
from datetime import datetime
from .base_market import BaseMarketFetcher
from ..config import get_settings

settings = get_settings()
COINGECKO_BASE = "https://api.coingecko.com/api/v3"


class CryptoFetcher(BaseMarketFetcher):

    def get_watchlist(self) -> list[str]:
        return settings.crypto_watchlist

    def get_exchange(self) -> str:
        return "CRYPTO"

    def get_asset_type(self) -> str:
        return "crypto"

    def _coin_id(self, ticker: str) -> str:
        return settings.crypto_id_map.get(ticker.upper(), ticker.lower())

    def fetch_ohlcv(self, ticker: str, period: str = "7d", interval: str = "1h") -> pd.DataFrame:
        try:
            coin_id = self._coin_id(ticker)
            days = 7
            url = f"{COINGECKO_BASE}/coins/{coin_id}/ohlc"
            resp = requests.get(url, params={"vs_currency": "usd", "days": days}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            df["volume"] = 0.0  # CoinGecko OHLC endpoint doesn't include volume
            return df
        except Exception as e:
            print(f"⚠️  Crypto OHLCV fetch failed for {ticker}: {e}")
            return pd.DataFrame()

    def fetch_current_price(self, ticker: str) -> dict:
        try:
            coin_id = self._coin_id(ticker)
            url = f"{COINGECKO_BASE}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true",
            }
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json().get(coin_id, {})
            price = data.get("usd", 0)
            return {
                "ticker": ticker,
                "price": round(float(price), 6),
                "volume": float(data.get("usd_24h_vol", 0)),
                "market_cap": float(data.get("usd_market_cap", 0)),
                "pct_change_24h": round(float(data.get("usd_24h_change", 0)), 2),
                "high_52w": 0,
                "low_52w": 0,
            }
        except Exception as e:
            print(f"⚠️  Crypto price fetch failed for {ticker}: {e}")
            return {"ticker": ticker, "price": 0, "volume": 0, "market_cap": 0,
                    "pct_change_24h": 0, "high_52w": 0, "low_52w": 0}
