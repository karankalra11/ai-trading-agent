"""
Lightweight VADER-based sentiment analyzer.
Used as the default on hosted/free environments where FinBERT (2GB) is too heavy.
VADER is 1MB, no GPU, no download — perfect for Render free tier.
"""
import math
from datetime import datetime, timezone

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
    VADER_AVAILABLE = True
except ImportError:
    _vader = None
    VADER_AVAILABLE = False


def _score_text(text: str) -> dict:
    """Returns {label, score, compound} for a single text."""
    if not VADER_AVAILABLE or not _vader:
        return {"label": "neutral", "score": 0.5, "compound": 0.0}
    scores = _vader.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return {"label": label, "score": abs(compound), "compound": compound}


class VaderSentimentAnalyzer:

    def aggregate_for_ticker(self, news_items: list[dict]) -> dict:
        if not news_items:
            return self._empty()

        now = datetime.now(timezone.utc)
        weights = []
        for item in news_items:
            pub = item.get("published_at")
            age_hours = 6.0
            if pub:
                try:
                    from dateutil import parser as dateparser
                    dt = dateparser.parse(pub) if isinstance(pub, str) else pub
                    if dt and dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if dt:
                        age_hours = max(0, (now - dt).total_seconds() / 3600)
                except Exception:
                    pass
            weights.append(math.exp(-age_hours / 6.0))

        total_weight = sum(weights) or 1.0
        weighted_score = 0.0
        pos_w = neg_w = neu_w = 0.0
        scored_items = []

        for i, item in enumerate(news_items):
            text = item.get("headline", "")
            if not text:
                continue
            result = _score_text(text)
            compound = result["compound"]
            label = result["label"]
            w = weights[i] if i < len(weights) else 1.0
            weighted_score += compound * w
            if label == "positive":
                pos_w += w
            elif label == "negative":
                neg_w += w
            else:
                neu_w += w
            scored_items.append({
                "headline": text,
                "label": label,
                "numeric": compound,
                "weight": w,
                "source": item.get("source", ""),
            })

        weighted_score /= total_weight
        top = sorted(scored_items, key=lambda x: abs(x["numeric"]), reverse=True)[:3]

        return {
            "weighted_score": round(weighted_score, 4),
            "positive_pct": round(pos_w / total_weight * 100, 1),
            "negative_pct": round(neg_w / total_weight * 100, 1),
            "neutral_pct": round(neu_w / total_weight * 100, 1),
            "item_count": len(scored_items),
            "top_headlines": [
                {"headline": t["headline"], "source": t["source"], "label": t["label"]}
                for t in top
            ],
        }

    def _empty(self) -> dict:
        return {
            "weighted_score": 0.0,
            "positive_pct": 0.0,
            "negative_pct": 0.0,
            "neutral_pct": 100.0,
            "item_count": 0,
            "top_headlines": [],
        }
