"""
Provider-agnostic AI brain for trading signal generation.

Supported providers (set AI_PROVIDER in .env):
  openrouter — OpenRouter free models  (FREE: any email, no card needed) ← RECOMMENDED
  gemini     — Google Gemini 2.0 Flash (FREE: Google account needed)
  groq       — Groq LLaMA 3.3 70B     (FREE: work email required)
  openai     — OpenAI GPT-4o mini      (paid, cheap ~$0.15/1M tokens)
  claude     — Anthropic Claude        (paid)

Default: openrouter
"""

import json
import time
import os
from .prompt_builder import PromptBuilder
from ..config import get_settings

settings = get_settings()


class SignalParseError(Exception):
    pass


# ── Shared JSON parse + validate (same for all providers) ─────────────────────

def _parse_and_validate(raw: str, ticker: str) -> dict:
    text = raw.strip()

    # Strip markdown code fences if present
    if "```" in text:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            text = text[start:end]

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                data = json.loads(text[start:end])
            except json.JSONDecodeError as e:
                raise SignalParseError(f"Cannot parse JSON for {ticker}: {e}\nRaw: {raw[:300]}")
        else:
            raise SignalParseError(f"No JSON block in response for {ticker}. Raw: {raw[:300]}")

    required = ["ticker", "signal", "entry_price", "confidence", "reasoning"]
    for field in required:
        if field not in data:
            raise SignalParseError(f"Missing '{field}' in response for {ticker}")

    data["signal"] = str(data.get("signal", "HOLD")).upper()
    if data["signal"] not in ("BUY", "SELL", "HOLD"):
        data["signal"] = "HOLD"

    if data["signal"] in ("BUY", "SELL") and data.get("target_price") and data.get("stop_loss"):
        _clamp_risk_reward(data)

    return data


def _clamp_risk_reward(signal: dict):
    entry = float(signal.get("entry_price") or 0)
    if entry <= 0:
        return
    max_sl = 0.15 if signal.get("asset_type") == "crypto" else 0.08
    if signal["signal"] == "BUY":
        if abs(entry - float(signal["stop_loss"])) / entry > max_sl:
            signal["stop_loss"] = round(entry * (1 - max_sl), 4)
    else:
        if abs(float(signal["stop_loss"]) - entry) / entry > max_sl:
            signal["stop_loss"] = round(entry * (1 + max_sl), 4)
    risk = abs(entry - float(signal.get("stop_loss") or entry))
    reward = abs(float(signal.get("target_price") or entry) - entry)
    if risk > 0:
        signal["risk_reward_ratio"] = round(reward / risk, 2)


# ── Gemini (FREE default) ──────────────────────────────────────────────────────

class GeminiBrain:
    """
    Uses the new google-genai SDK (google.genai).
    Free tier: 1,500 requests/day, no credit card needed.
    Get key: https://aistudio.google.com/app/apikey
    """

    def __init__(self):
        from google import genai
        from google.genai import types
        self._types = types
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.builder = PromptBuilder()
        self._system = self.builder.build_system_prompt()

    def generate_signal(self, ticker, exchange, asset_type, price_data, indicators, sentiment) -> dict:
        user_prompt = self.builder.build_user_prompt(
            ticker, exchange, asset_type, price_data, indicators, sentiment
        )
        config = self._types.GenerateContentConfig(
            temperature=0,
            max_output_tokens=1024,
            response_mime_type="application/json",
            system_instruction=self._system,
        )
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=settings.gemini_model,
                    contents=user_prompt,
                    config=config,
                )
                raw = response.text
                signal = _parse_and_validate(raw, ticker)
                signal["raw_claude_response"] = raw
                return signal
            except Exception as e:
                if attempt == 2:
                    raise SignalParseError(f"Gemini failed for {ticker}: {e}")
                time.sleep(2 ** attempt)
        raise SignalParseError("Gemini exhausted retries")


# ── Groq (FREE backup) ────────────────────────────────────────────────────────

class GroqBrain:
    """
    Uses groq SDK with LLaMA 3.3 70B (free).
    Free tier: 14,400 req/day, 6,000 tokens/min.
    Get key: https://console.groq.com  (no credit card)
    """

    def __init__(self):
        from groq import Groq
        self.client = Groq(api_key=settings.groq_api_key)
        self.builder = PromptBuilder()

    def generate_signal(self, ticker, exchange, asset_type, price_data, indicators, sentiment) -> dict:
        system = self.builder.build_system_prompt()
        user = self.builder.build_user_prompt(
            ticker, exchange, asset_type, price_data, indicators, sentiment
        )
        for attempt in range(3):
            try:
                resp = self.client.chat.completions.create(
                    model=settings.groq_model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0,
                    max_tokens=1024,
                    response_format={"type": "json_object"},
                )
                raw = resp.choices[0].message.content
                signal = _parse_and_validate(raw, ticker)
                signal["raw_claude_response"] = raw
                return signal
            except Exception as e:
                if attempt == 2:
                    raise SignalParseError(f"Groq failed for {ticker}: {e}")
                time.sleep(2 ** attempt)
        raise SignalParseError("Groq exhausted retries")


# ── OpenRouter (FREE — any email, no card) ────────────────────────────────────

class OpenRouterBrain:
    """
    OpenRouter gives access to many FREE models via one API.
    Works with ANY email — Gmail, personal, anything.
    No credit card needed for free models.

    Free models available:
      meta-llama/llama-3.3-70b-instruct:free
      deepseek/deepseek-r1:free
      mistralai/mistral-7b-instruct:free
      google/gemma-3-27b-it:free

    Get key: https://openrouter.ai  (sign up with any email)
    """

    OPENROUTER_BASE = "https://openrouter.ai/api/v1"

    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=self.OPENROUTER_BASE,
        )
        self.builder = PromptBuilder()

    def generate_signal(self, ticker, exchange, asset_type, price_data, indicators, sentiment) -> dict:
        system = self.builder.build_system_prompt()
        user = self.builder.build_user_prompt(
            ticker, exchange, asset_type, price_data, indicators, sentiment
        )
        for attempt in range(3):
            try:
                resp = self.client.chat.completions.create(
                    model=settings.openrouter_model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0,
                    max_tokens=1024,
                    extra_headers={
                        "HTTP-Referer": "https://ai-trading-agent.onrender.com",
                        "X-Title": "AI Trading Signal Agent",
                    },
                )
                raw = resp.choices[0].message.content
                signal = _parse_and_validate(raw, ticker)
                signal["raw_claude_response"] = raw
                return signal
            except Exception as e:
                if attempt == 2:
                    raise SignalParseError(f"OpenRouter failed for {ticker}: {e}")
                time.sleep(2 ** attempt)
        raise SignalParseError("OpenRouter exhausted retries")


# ── OpenAI (paid, cheap) ───────────────────────────────────────────────────────

class OpenAIBrain:
    """GPT-4o-mini: ~$0.15 per 1M input tokens."""

    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.builder = PromptBuilder()

    def generate_signal(self, ticker, exchange, asset_type, price_data, indicators, sentiment) -> dict:
        system = self.builder.build_system_prompt()
        user = self.builder.build_user_prompt(
            ticker, exchange, asset_type, price_data, indicators, sentiment
        )
        for attempt in range(3):
            try:
                resp = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0,
                    max_tokens=1024,
                    response_format={"type": "json_object"},
                )
                raw = resp.choices[0].message.content
                signal = _parse_and_validate(raw, ticker)
                signal["raw_claude_response"] = raw
                return signal
            except Exception as e:
                if attempt == 2:
                    raise SignalParseError(f"OpenAI failed for {ticker}: {e}")
                time.sleep(2 ** attempt)
        raise SignalParseError("OpenAI exhausted retries")


# ── Claude (original, paid) ────────────────────────────────────────────────────

class ClaudeBrain:
    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.builder = PromptBuilder()

    def generate_signal(self, ticker, exchange, asset_type, price_data, indicators, sentiment) -> dict:
        system = self.builder.build_system_prompt()
        user = self.builder.build_user_prompt(
            ticker, exchange, asset_type, price_data, indicators, sentiment
        )
        for attempt in range(3):
            try:
                response = self.client.messages.create(
                    model=settings.claude_model,
                    max_tokens=1024,
                    temperature=0,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                raw = response.content[0].text
                signal = _parse_and_validate(raw, ticker)
                signal["raw_claude_response"] = raw
                return signal
            except Exception as e:
                if attempt == 2:
                    raise SignalParseError(f"Claude failed for {ticker}: {e}")
                time.sleep(2 ** attempt)
        raise SignalParseError("Claude exhausted retries")


# ── Factory: picks brain based on AI_PROVIDER env var ─────────────────────────

def get_brain():
    """
    Returns the correct AI brain based on AI_PROVIDER setting.
    """
    provider = (settings.ai_provider or "openrouter").lower()

    if provider == "openrouter":
        if not settings.openrouter_api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set.\n"
                "Get a FREE key at: https://openrouter.ai\n"
                "Works with ANY email — Gmail, personal, anything. No credit card!"
            )
        return OpenRouterBrain()

    elif provider == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set.\n"
                "Get a FREE key at: https://aistudio.google.com/app/apikey\n"
                "No credit card needed!"
            )
        return GeminiBrain()

    elif provider == "groq":
        if not settings.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set.\n"
                "Get a FREE key at: https://console.groq.com\n"
                "No credit card needed!"
            )
        return GroqBrain()

    elif provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        return OpenAIBrain()

    elif provider == "claude":
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set.")
        return ClaudeBrain()

    else:
        raise RuntimeError(
            f"Unknown AI_PROVIDER='{provider}'. "
            "Choose: openrouter, gemini, groq, openai, claude"
        )
