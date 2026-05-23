import math
from datetime import datetime, timezone
from .model_loader import get_sentiment_pipeline


LABEL_SCORE = {"positive": 1.0, "negative": -1.0, "neutral": 0.0}


class SentimentAnalyzer:

    def analyze_batch(self, texts: list[str]) -> list[dict]:
        """Run FinBERT on a batch of texts. Returns [{label, score}]."""
        if not texts:
            return []
        pipe = get_sentiment_pipeline()
        try:
            results = pipe(texts, batch_size=16, truncation=True)
            return results  # list of {label, score}
        except Exception as e:
            print(f"⚠️  Sentiment batch failed: {e}")
            return [{"label": "neutral", "score": 0.5}] * len(texts)

    def aggregate_for_ticker(self, news_items: list[dict]) -> dict:
        """
        Run sentiment on all news headlines and aggregate into a single dict:
        {weighted_score, positive_pct, negative_pct, neutral_pct, item_count, top_headlines}
        """
        if not news_items:
            return self._empty()

        texts = [item.get("headline", "") for item in news_items if item.get("headline")]
        if not texts:
            return self._empty()

        raw_results = self.analyze_batch(texts)

        # Compute recency weights
        now = datetime.now(timezone.utc)
        weights = []
        for item in news_items:
            pub = item.get("published_at")
            age_hours = 6.0  # default if unknown
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
            weights.append(math.exp(-age_hours / 6.0))  # half-life = 6h

        total_weight = sum(weights) or 1.0
        weighted_score = 0.0
        pos_w = neg_w = neu_w = 0.0

        scored_items = []
        for i, res in enumerate(raw_results):
            label = res.get("label", "neutral").lower()
            conf = float(res.get("score", 0.5))
            numeric = LABEL_SCORE.get(label, 0.0) * conf
            w = weights[i] if i < len(weights) else 1.0

            weighted_score += numeric * w
            if label == "positive":
                pos_w += w
            elif label == "negative":
                neg_w += w
            else:
                neu_w += w

            scored_items.append({
                "headline": texts[i],
                "label": label,
                "numeric": numeric,
                "weight": w,
                "source": news_items[i].get("source", ""),
            })

        weighted_score /= total_weight

        # Top 3 headlines by absolute sentiment magnitude
        top = sorted(scored_items, key=lambda x: abs(x["numeric"]), reverse=True)[:3]

        return {
            "weighted_score": round(weighted_score, 4),
            "positive_pct": round(pos_w / total_weight * 100, 1),
            "negative_pct": round(neg_w / total_weight * 100, 1),
            "neutral_pct": round(neu_w / total_weight * 100, 1),
            "item_count": len(texts),
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
