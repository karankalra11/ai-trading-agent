"""
NewsData.io fetcher — free tier: 200 requests/day, 10 articles per request.
API docs: https://newsdata.io/documentation
"""
import requests
from datetime import datetime, timedelta
from ..config import get_settings

settings = get_settings()
NEWSDATA_BASE = "https://newsdata.io/api/1/latest"


class NewsDataFetcher:

    def __init__(self):
        self.api_key = settings.newsdata_api_key
        self.enabled = bool(self.api_key)

    def fetch_for_ticker(self, ticker: str, max_items: int = 10) -> list[dict]:
        if not self.enabled:
            return []

        clean = ticker.replace(".NS", "").replace(".BO", "")
        # Map crypto tickers to full names for better results
        crypto_map = {"BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana",
                      "BNB": "Binance", "XRP": "Ripple"}
        query = crypto_map.get(clean, clean)

        try:
            resp = requests.get(
                NEWSDATA_BASE,
                params={
                    "apikey": self.api_key,
                    "q": query,
                    "language": "en",
                    "category": "business,technology",
                    "size": max_items,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "success":
                print(f"⚠️  NewsData.io error for {ticker}: {data.get('message','unknown')}")
                return []

            return [self._parse(a) for a in (data.get("results") or []) if a]

        except Exception as e:
            print(f"⚠️  NewsData.io fetch failed for {ticker}: {e}")
            return []

    def _parse(self, article: dict) -> dict:
        return {
            "headline": (article.get("title") or "").strip(),
            "url": article.get("link") or article.get("source_url") or "",
            "published_at": article.get("pubDate"),
            "source": article.get("source_id") or "newsdata",
            "source_type": "newsdata",
            "description": (article.get("description") or "")[:300],
        }
