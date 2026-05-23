import json
import time
import anthropic
from .prompt_builder import PromptBuilder
from ..config import get_settings

settings = get_settings()


class SignalParseError(Exception):
    pass


class ClaudeBrain:

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.builder = PromptBuilder()

    def generate_signal(
        self,
        ticker: str,
        exchange: str,
        asset_type: str,
        price_data: dict,
        indicators: dict,
        sentiment: dict,
    ) -> dict:
        system = self.builder.build_system_prompt()
        user = self.builder.build_user_prompt(
            ticker, exchange, asset_type, price_data, indicators, sentiment
        )

        raw = self._call_claude(system, user)
        signal = self._parse_response(raw, ticker)
        signal["raw_claude_response"] = raw
        return signal

    def _call_claude(self, system: str, user: str, retries: int = 3) -> str:
        for attempt in range(retries):
            try:
                response = self.client.messages.create(
                    model=settings.claude_model,
                    max_tokens=1024,
                    temperature=0,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                return response.content[0].text
            except anthropic.RateLimitError:
                wait = 2 ** attempt
                print(f"⚠️  Claude rate limited, retrying in {wait}s…")
                time.sleep(wait)
            except Exception as e:
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)
        raise SignalParseError("Claude API failed after retries")

    def _parse_response(self, raw: str, ticker: str) -> dict:
        # Extract JSON from response (handle markdown code blocks)
        text = raw.strip()
        if "```" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            text = text[start:end]

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Try to find first { ... } block
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    data = json.loads(text[start:end])
                except json.JSONDecodeError as e:
                    raise SignalParseError(f"Could not parse Claude JSON for {ticker}: {e}")
            else:
                raise SignalParseError(f"No JSON found in Claude response for {ticker}")

        # Validate required fields
        required = ["ticker", "signal", "entry_price", "confidence", "reasoning"]
        for field in required:
            if field not in data:
                raise SignalParseError(f"Missing field '{field}' in Claude response for {ticker}")

        # Normalise signal
        data["signal"] = data["signal"].upper()
        if data["signal"] not in ("BUY", "SELL", "HOLD"):
            data["signal"] = "HOLD"

        # Validate risk/reward
        if data["signal"] in ("BUY", "SELL") and data.get("target_price") and data.get("stop_loss"):
            self._validate_risk_reward(data, asset_type=data.get("asset_type", "stock"))

        return data

    def _validate_risk_reward(self, signal: dict, asset_type: str = "stock"):
        entry = float(signal.get("entry_price") or 0)
        target = float(signal.get("target_price") or 0)
        stop = float(signal.get("stop_loss") or 0)

        if entry <= 0:
            return

        max_sl_pct = 0.15 if asset_type == "crypto" else 0.08

        if signal["signal"] == "BUY":
            sl_pct = abs(entry - stop) / entry
            if sl_pct > max_sl_pct:
                # Clamp stop-loss
                signal["stop_loss"] = round(entry * (1 - max_sl_pct), 4)
        elif signal["signal"] == "SELL":
            sl_pct = abs(stop - entry) / entry
            if sl_pct > max_sl_pct:
                signal["stop_loss"] = round(entry * (1 + max_sl_pct), 4)

        # Recalculate R:R
        entry = float(signal["entry_price"])
        target = float(signal.get("target_price") or entry)
        stop = float(signal.get("stop_loss") or entry)
        risk = abs(entry - stop)
        reward = abs(target - entry)
        if risk > 0:
            signal["risk_reward_ratio"] = round(reward / risk, 2)
