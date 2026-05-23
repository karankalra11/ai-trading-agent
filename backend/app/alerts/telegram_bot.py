import requests
from ..config import get_settings

settings = get_settings()

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramAlerter:

    def __init__(self):
        self.token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.enabled = bool(self.token and self.chat_id)

    def send_signal_alert(self, signal: dict) -> bool:
        if not self.enabled:
            return False
        confidence = signal.get("confidence") or 0
        if confidence < settings.min_confidence_alert:
            return False
        message = self._format_message(signal)
        return self._send(message)

    def send_daily_summary(self, signals: list[dict]) -> bool:
        if not self.enabled or not signals:
            return False
        buy = [s for s in signals if s.get("signal") == "BUY"]
        sell = [s for s in signals if s.get("signal") == "SELL"]
        hold = [s for s in signals if s.get("signal") == "HOLD"]

        lines = [
            "📊 *Daily Signal Summary*",
            f"🟢 BUY: {len(buy)} | 🔴 SELL: {len(sell)} | ⚪ HOLD: {len(hold)}",
            "",
        ]
        for s in sorted(signals, key=lambda x: x.get("confidence") or 0, reverse=True)[:5]:
            emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}.get(s.get("signal", "HOLD"), "⚪")
            lines.append(f"{emoji} {s.get('ticker')} — {s.get('confidence')}% conf")

        return self._send("\n".join(lines))

    def _format_message(self, signal: dict) -> str:
        sig = signal.get("signal", "HOLD")
        emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}.get(sig, "⚪")
        ticker = signal.get("ticker", "")
        exchange = signal.get("exchange", "")
        entry = signal.get("entry_price") or "—"
        target = signal.get("target_price") or "—"
        stop = signal.get("stop_loss") or "—"
        conf = signal.get("confidence") or "—"
        tf = (signal.get("timeframe") or "").upper()
        rr = signal.get("risk_reward_ratio") or "—"
        reasoning = (signal.get("reasoning") or "")[:200]
        risks = signal.get("key_risks") or []
        risk_text = " | ".join(risks[:2]) if risks else "—"

        return (
            f"{emoji} *{sig} Signal — {ticker}* ({exchange})\n"
            f"💰 Entry: `{entry}` | Target: `{target}` | SL: `{stop}`\n"
            f"📊 Confidence: *{conf}%* | Timeframe: {tf} | R:R {rr}x\n"
            f"💬 _{reasoning}_\n"
            f"⚠️ Risks: {risk_text}"
        )

    def _send(self, message: str) -> bool:
        try:
            url = TELEGRAM_API.format(token=self.token)
            resp = requests.post(
                url,
                json={"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"⚠️  Telegram send failed: {e}")
            return False
