from .us_stocks import USStockFetcher
from ..config import get_settings

settings = get_settings()


class ETFFetcher(USStockFetcher):
    """ETF fetcher — same as US stocks but different watchlist and asset_type."""

    def get_watchlist(self) -> list[str]:
        return settings.etf_watchlist

    def get_exchange(self) -> str:
        return "NYSE"

    def get_asset_type(self) -> str:
        return "etf"
