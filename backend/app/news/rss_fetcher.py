from __future__ import annotations
import feedparser
import requests
from datetime import datetime, timezone
from urllib.parse import quote

RSS_FEEDS = {
    "yahoo_finance": "https://finance.yahoo.com/rss/headline?s={ticker}",
    "google_news": "https://news.google.com/rss/search?q={query}+stock+finance&hl=en-US&gl=US&ceid=US:en",
    "motley_fool": "https://www.fool.com/feeds/index.aspx",
    "seeking_alpha": "https://seekingalpha.com/feed.xml",
}


class RSSFetcher:

    def fetch_for_ticker(self, ticker: str, max_items: int = 15) -> list[dict]:
        items = []
        clean = ticker.replace(".NS", "").replace(".BO", "")

        # Yahoo Finance RSS
        try:
            url = RSS_FEEDS["yahoo_finance"].format(ticker=clean)
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_items]:
                items.append(self._parse_entry(entry, "yahoo_rss"))
        except Exception:
            pass

        # Google News RSS
        try:
            query = quote(clean)
            url = RSS_FEEDS["google_news"].format(query=query)
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_items]:
                items.append(self._parse_entry(entry, "google_news"))
        except Exception:
            pass

        return [i for i in items if i]

    def fetch_global_feeds(self, max_items: int = 10) -> list[dict]:
        items = []
        for name in ["motley_fool", "seeking_alpha"]:
            try:
                feed = feedparser.parse(RSS_FEEDS[name])
                for entry in feed.entries[:max_items]:
                    items.append(self._parse_entry(entry, name))
            except Exception:
                pass
        return [i for i in items if i]

    def _parse_entry(self, entry, source: str) -> dict | None:
        try:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
            return {
                "headline": entry.get("title", "").strip(),
                "url": entry.get("link", ""),
                "published_at": published,
                "source": source,
                "source_type": "rss",
            }
        except Exception:
            return None
