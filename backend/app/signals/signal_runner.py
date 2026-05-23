from __future__ import annotations
"""
SignalRunner: orchestrates the full pipeline for each ticker.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Signal, PriceSnapshot, NewsSentiment
from ..data.us_stocks import USStockFetcher
from ..data.india_stocks import IndiaStockFetcher
from ..data.crypto import CryptoFetcher
from ..data.etfs import ETFFetcher
from ..indicators.technical import TechnicalAnalyzer
from ..news.news_aggregator import NewsAggregator
# Use VADER (lightweight) in hosted/lite mode, FinBERT locally if available
import os
if os.getenv("USE_FINBERT", "false").lower() == "true":
    from ..sentiment.analyzer import SentimentAnalyzer as _SentimentAnalyzer
else:
    from ..sentiment.vader_analyzer import VaderSentimentAnalyzer as _SentimentAnalyzer
from .ai_brain import get_brain, SignalParseError
from ..config import get_settings

settings = get_settings()


class SignalRunner:

    def __init__(self):
        self.fetchers = {
            "us": USStockFetcher(),
            "india": IndiaStockFetcher(),
            "crypto": CryptoFetcher(),
            "etf": ETFFetcher(),
        }
        self.technical = TechnicalAnalyzer()
        self.news_agg = NewsAggregator()
        self.sentiment = _SentimentAnalyzer()
        self.brain = get_brain()

    def run_for_ticker(self, ticker: str, market: str) -> dict | None:
        fetcher = self.fetchers[market]
        exchange = fetcher.get_exchange()
        asset_type = fetcher.get_asset_type()

        print(f"\n⚙️  Processing {ticker} ({exchange}) …")

        # 1. Price + OHLCV
        price_data = fetcher.fetch_current_price(ticker)
        if not price_data.get("price"):
            print(f"  ⚠️  Skipping {ticker} — no price data")
            return None

        ohlcv = fetcher.fetch_ohlcv(ticker)
        indicators = self.technical.compute_all(ohlcv) if not ohlcv.empty else {}

        # 2. News + Sentiment
        news_items = self.news_agg.gather_for_ticker(ticker)
        sentiment = self.sentiment.aggregate_for_ticker(news_items)

        # 3. Claude signal
        try:
            signal_data = self.brain.generate_signal(
                ticker, exchange, asset_type, price_data, indicators, sentiment
            )
        except SignalParseError as e:
            print(f"  ❌ Claude parse error for {ticker}: {e}")
            return None
        except Exception as e:
            print(f"  ❌ Claude error for {ticker}: {e}")
            return None

        # 4. Persist to DB
        self._save_signal(signal_data, price_data, indicators, news_items, sentiment)

        emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}.get(signal_data.get("signal", "HOLD"), "⚪")
        print(f"  {emoji} {signal_data.get('signal')} | conf: {signal_data.get('confidence')}% | {signal_data.get('reasoning', '')[:80]}")
        return signal_data

    def run_all_watchlists(self) -> list[dict]:
        all_signals = []
        watchlists = {
            "us": self.fetchers["us"].get_watchlist(),
            "india": self.fetchers["india"].get_watchlist(),
            "crypto": self.fetchers["crypto"].get_watchlist(),
            "etf": self.fetchers["etf"].get_watchlist(),
        }
        for market, tickers in watchlists.items():
            for ticker in tickers:
                result = self.run_for_ticker(ticker, market)
                if result:
                    all_signals.append(result)

        # Send Telegram alerts for high-confidence signals
        high_conf = [s for s in all_signals if (s.get("confidence") or 0) >= settings.min_confidence_alert]
        if high_conf:
            from ..alerts.telegram_bot import TelegramAlerter
            alerter = TelegramAlerter()
            for sig in high_conf:
                alerter.send_signal_alert(sig)

        return all_signals

    def _save_signal(self, signal_data: dict, price_data: dict, indicators: dict,
                     news_items: list[dict], sentiment: dict):
        db: Session = SessionLocal()
        try:
            sig = Signal(
                ticker=signal_data.get("ticker", ""),
                exchange=signal_data.get("exchange", ""),
                asset_type=signal_data.get("asset_type", ""),
                signal=signal_data.get("signal", "HOLD"),
                entry_price=signal_data.get("entry_price"),
                target_price=signal_data.get("target_price"),
                stop_loss=signal_data.get("stop_loss"),
                confidence=signal_data.get("confidence"),
                reasoning=signal_data.get("reasoning"),
                timeframe=signal_data.get("timeframe"),
                data_sources=signal_data.get("data_sources"),
                risk_reward_ratio=signal_data.get("risk_reward_ratio"),
                key_risks=signal_data.get("key_risks"),
                raw_claude_response=signal_data.get("raw_claude_response"),
            )
            db.add(sig)

            snap = PriceSnapshot(
                ticker=signal_data.get("ticker", ""),
                open=price_data.get("price"),
                high=price_data.get("high_52w"),
                low=price_data.get("low_52w"),
                close=price_data.get("price"),
                volume=price_data.get("volume"),
                rsi_14=indicators.get("rsi_14"),
                macd=indicators.get("macd"),
                macd_signal=indicators.get("macd_signal_line"),
                bb_upper=indicators.get("bb_upper"),
                bb_lower=indicators.get("bb_lower"),
                ema_20=indicators.get("ema_20"),
                ema_50=indicators.get("ema_50"),
            )
            db.add(snap)

            for item in news_items[:20]:
                ns = NewsSentiment(
                    ticker=signal_data.get("ticker", ""),
                    headline=item.get("headline", ""),
                    source=item.get("source"),
                    url=item.get("url"),
                    published_at=None,
                    sentiment_label=None,
                    sentiment_score=None,
                    source_type=item.get("source_type"),
                )
                db.add(ns)

            db.commit()
        except Exception as e:
            db.rollback()
            print(f"  ⚠️  DB save error: {e}")
        finally:
            db.close()
