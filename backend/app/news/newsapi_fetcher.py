import requests
from datetime import datetime, timedelta
from ..config import get_settings

settings = get_settings()
NEWSAPI_BASE = "https://newsapi.org/v2"


class NewsAPIFetcher:

    def __init__(self):
        self.api_key = settings.newsapi_key
        self.enabled = bool(self.api_key)

    def fetch_for_ticker(self, ticker: str, hours_back: int = 24) -> list[dict]:
        if not self.enabled:
            return []
        clean = ticker.replace(".NS", "").replace(".BO", "")
        from_date = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            resp = requests.get(
                f"{NEWSAPI_BASE}/everything",
                params={
                    "q": f"{clean} stock",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "from": from_date,
                    "pageSize": 20,
                    "apiKey": self.api_key,
                },
                timeout=10,
            )
            resp.raise_for_status()
            articles = resp.json().get("articles", [])
            return [self._parse_article(a) for a in articles if a]
        except Exception as e:
            print(f"⚠️  NewsAPI fetch failed for {ticker}: {e}")
            return []

    def _parse_article(self, article: dict) -> dict:
        return {
            "headline": article.get("title", "").strip(),
            "url": article.get("url", ""),
            "published_at": article.get("publishedAt"),
            "source": article.get("source", {}).get("name", "newsapi"),
            "source_type": "newsapi",
        }
