from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from hashlib import md5
from .rss_fetcher import RSSFetcher
from .newsapi_fetcher import NewsAPIFetcher
from .newsdata_fetcher import NewsDataFetcher
from .twitter_fetcher import TwitterFetcher


class NewsAggregator:

    def __init__(self):
        self.rss = RSSFetcher()
        self.newsapi = NewsAPIFetcher()
        self.newsdata = NewsDataFetcher()
        self.twitter = TwitterFetcher()

    def gather_for_ticker(self, ticker: str, hours_back: int = 12) -> list[dict]:
        all_items = []

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {
                pool.submit(self.rss.fetch_for_ticker, ticker): "rss",
                pool.submit(self.newsapi.fetch_for_ticker, ticker, hours_back): "newsapi",
                pool.submit(self.newsdata.fetch_for_ticker, ticker): "newsdata",
                pool.submit(self.twitter.fetch_for_ticker, ticker): "twitter",
            }
            for future in as_completed(futures):
                try:
                    all_items.extend(future.result())
                except Exception:
                    pass

        all_items = self._filter_recent(all_items, hours_back)
        all_items = self._deduplicate(all_items)
        return all_items

    def _filter_recent(self, items: list[dict], hours: int) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        result = []
        for item in items:
            pub = item.get("published_at")
            if not pub:
                result.append(item)  # keep items with unknown date
                continue
            try:
                if isinstance(pub, str):
                    from dateutil import parser as dateparser
                    dt = dateparser.parse(pub)
                    if dt and dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if dt and dt >= cutoff:
                        result.append(item)
                else:
                    result.append(item)
            except Exception:
                result.append(item)
        return result

    def _deduplicate(self, items: list[dict]) -> list[dict]:
        seen = set()
        result = []
        for item in items:
            key = md5((item.get("url") or item.get("headline", "")).encode()).hexdigest()
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result
