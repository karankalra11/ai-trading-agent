from __future__ import annotations
"""
Twitter/X scraping via requests + nitter public instances.
No API key required. Falls back gracefully if unavailable.
"""
import requests
import feedparser
from datetime import datetime, timezone


NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
]


class TwitterFetcher:

    def fetch_for_ticker(self, ticker: str, limit: int = 20) -> list[dict]:
        clean = ticker.replace(".NS", "").replace(".BO", "")
        query = f"${clean} OR {clean} stock lang:en"
        items = []

        for instance in NITTER_INSTANCES:
            try:
                url = f"{instance}/search/rss?f=tweets&q={requests.utils.quote(query)}"
                feed = feedparser.parse(url)
                if feed.entries:
                    for entry in feed.entries[:limit]:
                        items.append(self._parse_entry(entry))
                    break  # success — stop trying instances
            except Exception:
                continue

        return [i for i in items if i]

    def _parse_entry(self, entry) -> dict | None:
        try:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
            text = entry.get("title", "") or entry.get("summary", "")
            return {
                "headline": text.strip()[:280],
                "url": entry.get("link", ""),
                "published_at": published,
                "source": "twitter",
                "source_type": "twitter",
            }
        except Exception:
            return None
