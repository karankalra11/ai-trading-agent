class PromptBuilder:

    def build_system_prompt(self) -> str:
        return """You are an expert quantitative trading analyst with deep expertise in technical analysis,
fundamental valuation, and market sentiment interpretation.

Your task is to synthesize multiple data signals and produce precise, actionable trading recommendations.

## Rules you MUST follow:
1. Output ONLY valid JSON — no prose, no markdown, no text outside the JSON block.
2. Be conservative: prefer HOLD when signals conflict or are unclear.
3. Never recommend a signal with confidence below 40.
4. Stop-loss must not exceed 8% distance from entry price (15% for crypto).
5. Target must offer at least 1.5x risk/reward ratio.
6. risk_reward_ratio = (target_price - entry_price) / (entry_price - stop_loss) for BUY.
7. For SELL signals: risk_reward_ratio = (entry_price - target_price) / (stop_loss - entry_price).
8. For HOLD: set entry_price = current price, target_price = null, stop_loss = null, risk_reward_ratio = null.
9. Key risks must be specific, not generic — mention the actual company/market context."""

    def build_user_prompt(
        self,
        ticker: str,
        exchange: str,
        asset_type: str,
        price_data: dict,
        indicators: dict,
        sentiment: dict,
    ) -> str:
        interp = indicators.get("interpretations", {})

        # Format top headlines
        headlines_text = ""
        for i, h in enumerate(sentiment.get("top_headlines", [])[:3], 1):
            label_emoji = "📈" if h.get("label") == "positive" else "📉" if h.get("label") == "negative" else "➡️"
            headlines_text += f'  {i}. {label_emoji} "{h.get("headline", "")}" [{h.get("source", "")}]\n'
        if not headlines_text:
            headlines_text = "  No recent headlines available.\n"

        price = price_data.get("price", 0)
        market_cap_b = round(price_data.get("market_cap", 0) / 1e9, 2)

        prompt = f"""Analyze the following data for **{ticker}** ({exchange}, {asset_type.upper()}) and generate a trading signal.

## Current Price Data
- Current Price: {price}
- 24h Change: {price_data.get("pct_change_24h", 0):+.2f}%
- Market Cap: ${market_cap_b}B
- 52-week High: {price_data.get("high_52w", "N/A")} | Low: {price_data.get("low_52w", "N/A")}

## Technical Indicators
- RSI(14): {indicators.get("rsi_14", "N/A")} → {interp.get("rsi_summary", "")}
- MACD: {indicators.get("macd", "N/A")} / Signal Line: {indicators.get("macd_signal_line", "N/A")} → {interp.get("macd_summary", "")}
- Bollinger Bands: Upper {indicators.get("bb_upper", "N/A")} | Lower {indicators.get("bb_lower", "N/A")} | %B: {indicators.get("bb_pct_b", "N/A")} → {interp.get("bb_summary", "")}
- EMA 20: {indicators.get("ema_20", "N/A")} | EMA 50: {indicators.get("ema_50", "N/A")} | {interp.get("ema_summary", "")}
- Volume Ratio (vs 10d avg): {indicators.get("volume_ratio", "N/A")}x → {interp.get("volume_summary", "")}
- ATR(14): {indicators.get("atr_14", "N/A")}

## Market Sentiment (last 12 hours, {sentiment.get("item_count", 0)} news items)
- Weighted Sentiment Score: {sentiment.get("weighted_score", 0):.4f} (range: -1.0 bearish → +1.0 bullish)
- Breakdown: Positive {sentiment.get("positive_pct", 0):.1f}% | Negative {sentiment.get("negative_pct", 0):.1f}% | Neutral {sentiment.get("neutral_pct", 0):.1f}%
- Top Headlines:
{headlines_text}
## Respond with ONLY this JSON (no markdown, no extra text):
{{
  "ticker": "{ticker}",
  "exchange": "{exchange}",
  "asset_type": "{asset_type}",
  "signal": "BUY or SELL or HOLD",
  "entry_price": <current price as number>,
  "target_price": <target price as number or null for HOLD>,
  "stop_loss": <stop loss as number or null for HOLD>,
  "confidence": <integer 0-100>,
  "reasoning": "<2-3 sentences explaining key drivers for this signal>",
  "timeframe": "short or mid or long",
  "data_sources": ["technical", "sentiment"],
  "risk_reward_ratio": <number or null for HOLD>,
  "key_risks": ["<specific risk 1>", "<specific risk 2>"]
}}"""
        return prompt
