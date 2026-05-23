from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",          # silently ignore unknown env vars like USE_FINBERT
    )

    # AI provider — choose: openrouter (FREE, any email), gemini, groq, openai, claude
    ai_provider: str = "openrouter"

    # OpenRouter (FREE — any email, no card) — https://openrouter.ai
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-oss-120b:free"

    # Gemini (FREE default) — https://aistudio.google.com/app/apikey
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Groq (FREE backup) — https://console.groq.com
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # OpenAI (paid, cheap) — https://platform.openai.com
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Claude / Anthropic (paid)
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-5"

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # News
    newsapi_key: str = ""
    newsdata_api_key: str = ""   # newsdata.io — free 200 req/day

    # Database
    database_url: str = "sqlite:///./trading.db"

    # Scheduler
    schedule_interval_min: int = 30
    min_confidence_alert: int = 75

    # Sentiment model
    sentiment_model: str = "ProsusAI/finbert"

    # Watchlists (~50 tickers total)
    us_watchlist: list[str] = [
        "AAPL", "NVDA", "MSFT", "TSLA", "META", "GOOGL", "AMZN",
        "JPM", "V", "JNJ", "WMT", "XOM", "BAC", "MA", "PG",
        "NFLX", "AMD", "ORCL", "UBER", "COIN",
    ]
    india_watchlist: list[str] = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "WIPRO.NS",
        "ICICIBANK.NS", "HINDUNILVR.NS", "BAJFINANCE.NS", "SBIN.NS",
        "ADANIENT.NS", "TATAMOTORS.NS", "ZOMATO.NS",
    ]
    crypto_watchlist: list[str] = [
        "BTC", "ETH", "SOL", "BNB", "XRP",
        "ADA", "DOGE", "AVAX", "DOT", "LINK",
    ]
    etf_watchlist: list[str] = [
        "SPY", "QQQ", "GLD", "VTI", "ARKK",
        "IWM", "DIA", "XLF", "XLK", "SLV",
    ]

    # CoinGecko coin ID map
    crypto_id_map: dict = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "AVAX": "avalanche-2",
        "DOT": "polkadot",
        "LINK": "chainlink",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
