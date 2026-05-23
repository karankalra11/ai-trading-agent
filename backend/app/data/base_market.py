from abc import ABC, abstractmethod
import pandas as pd


class BaseMarketFetcher(ABC):
    """Abstract base class for all market data fetchers."""

    @abstractmethod
    def fetch_ohlcv(self, ticker: str, period: str = "5d", interval: str = "30m") -> pd.DataFrame:
        """Return OHLCV DataFrame with columns: open, high, low, close, volume."""
        ...

    @abstractmethod
    def fetch_current_price(self, ticker: str) -> dict:
        """Return dict with price, volume, market_cap, pct_change_24h, high_52w, low_52w."""
        ...

    @abstractmethod
    def get_watchlist(self) -> list[str]:
        """Return list of ticker symbols to track."""
        ...

    def get_exchange(self) -> str:
        return "UNKNOWN"

    def get_asset_type(self) -> str:
        return "stock"
