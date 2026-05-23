"""
Loads FinBERT once at startup and caches as a singleton.
ProsusAI/finbert returns: positive / negative / neutral labels.
"""
from transformers import pipeline
from ..config import get_settings

settings = get_settings()

_pipeline = None


def get_sentiment_pipeline():
    global _pipeline
    if _pipeline is None:
        print(f"🤖 Loading sentiment model: {settings.sentiment_model} …")
        _pipeline = pipeline(
            "text-classification",
            model=settings.sentiment_model,
            tokenizer=settings.sentiment_model,
            truncation=True,
            max_length=512,
            device=-1,  # CPU; set to 0 for GPU
        )
        print("✅ Sentiment model loaded")
    return _pipeline
