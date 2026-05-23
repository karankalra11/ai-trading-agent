from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",          # silently ignore unknown env vars like USE_FINBERT
    )

    # AI provider — choose: gemini (FREE), groq (FREE), openai, claude
    ai_provider: str = "gemini"

    # Gemini (FREE default) — https://aistudio.google.com/app/apikey
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

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

    # Database
    database_url: str = "sqlite:///./trading.db"

    # Scheduler
    schedule_interval_min: int = 30
    min_confidence_alert: int = 75

    # Sentiment model
    sentiment_model: str = "ProsusAI/finbert"

    # Watchlists
    us_watchlist: list[str] = ["AAPL", "NVDA", "MSFT", "TSLA", "META", "GOOGL", "AMZN"]
    india_watchlist: list[str] = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "WIPRO.NS"]
    crypto_watchlist: list[str] = ["BTC", "ETH", "SOL", "BNB", "XRP"]
    etf_watchlist: list[str] = ["SPY", "QQQ", "GLD", "VTI", "ARKK"]

    # CoinGecko coin ID map
    crypto_id_map: dict = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "BNB": "binancecoin",
        "XRP": "ripple",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
