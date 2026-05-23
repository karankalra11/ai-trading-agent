"""
Technical indicators implemented in pure pandas/numpy.
No pandas-ta, no numba, no C compiler — works on any free host.
"""
import pandas as pd
import numpy as np


class TechnicalAnalyzer:

    def compute_all(self, df: pd.DataFrame) -> dict:
        if df.empty or len(df) < 20:
            return {}

        result = {}
        for fn in [
            self.compute_rsi,
            self.compute_macd,
            self.compute_bollinger,
            self.compute_ema,
            self.compute_volume,
            self.compute_atr,
        ]:
            try:
                result.update(fn(df))
            except Exception:
                pass

        result["interpretations"] = self.interpret_signals(result)
        return result

    # ── RSI ───────────────────────────────────────────────────────────────────
    def compute_rsi(self, df: pd.DataFrame, length: int = 14) -> dict:
        close = df["close"].astype(float)
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(com=length - 1, min_periods=length).mean()
        avg_loss = loss.ewm(com=length - 1, min_periods=length).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        val = float(rsi.iloc[-1]) if not rsi.empty else 50.0
        if np.isnan(val):
            val = 50.0
        signal = "overbought" if val >= 70 else "oversold" if val <= 30 else "neutral"
        return {"rsi_14": round(val, 2), "rsi_signal": signal}

    # ── MACD ──────────────────────────────────────────────────────────────────
    def compute_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
        close = df["close"].astype(float)
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        macd_val = float(macd_line.iloc[-1])
        signal_val = float(signal_line.iloc[-1])
        hist_val = float(histogram.iloc[-1])
        trend = "bullish" if macd_val > signal_val else "bearish"
        return {
            "macd": round(macd_val, 4),
            "macd_signal_line": round(signal_val, 4),
            "macd_histogram": round(hist_val, 4),
            "macd_trend": trend,
        }

    # ── Bollinger Bands ───────────────────────────────────────────────────────
    def compute_bollinger(self, df: pd.DataFrame, length: int = 20, std: float = 2.0) -> dict:
        close = df["close"].astype(float)
        mid = close.rolling(length).mean()
        sigma = close.rolling(length).std()
        upper = mid + std * sigma
        lower = mid - std * sigma
        bandwidth = ((upper - lower) / mid).iloc[-1]
        price = close.iloc[-1]
        band_range = float(upper.iloc[-1]) - float(lower.iloc[-1])
        pct_b = (price - float(lower.iloc[-1])) / band_range if band_range != 0 else 0.5
        return {
            "bb_upper": round(float(upper.iloc[-1]), 4),
            "bb_middle": round(float(mid.iloc[-1]), 4),
            "bb_lower": round(float(lower.iloc[-1]), 4),
            "bb_bandwidth": round(float(bandwidth), 4),
            "bb_pct_b": round(float(pct_b), 4),
        }

    # ── EMA ───────────────────────────────────────────────────────────────────
    def compute_ema(self, df: pd.DataFrame) -> dict:
        close = df["close"].astype(float)
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()
        e20 = float(ema20.iloc[-1])
        e50 = float(ema50.iloc[-1])

        crossover = "none"
        if len(df) >= 51:
            prev_e20 = float(ema20.iloc[-2])
            prev_e50 = float(ema50.iloc[-2])
            if prev_e20 <= prev_e50 and e20 > e50:
                crossover = "golden_cross"
            elif prev_e20 >= prev_e50 and e20 < e50:
                crossover = "death_cross"
            elif e20 > e50:
                crossover = "above"
            else:
                crossover = "below"

        return {"ema_20": round(e20, 4), "ema_50": round(e50, 4), "ema_crossover": crossover}

    # ── Volume ────────────────────────────────────────────────────────────────
    def compute_volume(self, df: pd.DataFrame) -> dict:
        if "volume" not in df.columns or df["volume"].sum() == 0:
            return {"avg_volume_10d": 0, "current_volume": 0, "volume_ratio": 1.0}
        avg_vol = float(df["volume"].tail(10).mean())
        curr_vol = float(df["volume"].iloc[-1])
        ratio = round(curr_vol / avg_vol, 2) if avg_vol > 0 else 1.0
        return {"avg_volume_10d": int(avg_vol), "current_volume": int(curr_vol), "volume_ratio": ratio}

    # ── ATR ───────────────────────────────────────────────────────────────────
    def compute_atr(self, df: pd.DataFrame, length: int = 14) -> dict:
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        close = df["close"].astype(float)
        prev_close = close.shift(1)
        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ], axis=1).max(axis=1)
        atr = tr.ewm(span=length, adjust=False).mean()
        val = float(atr.iloc[-1]) if not atr.empty else 0.0
        return {"atr_14": round(val, 4)}

    # ── Interpretations ───────────────────────────────────────────────────────
    def interpret_signals(self, indicators: dict) -> dict:
        interp = {}

        rsi = indicators.get("rsi_14", 50)
        if rsi >= 70:
            interp["rsi_summary"] = f"RSI {rsi:.1f} — overbought, watch for reversal"
        elif rsi <= 30:
            interp["rsi_summary"] = f"RSI {rsi:.1f} — oversold, potential bounce"
        else:
            interp["rsi_summary"] = f"RSI {rsi:.1f} — neutral range"

        macd_trend = indicators.get("macd_trend", "neutral")
        hist = indicators.get("macd_histogram", 0)
        interp["macd_summary"] = f"MACD {macd_trend}, histogram {hist:+.4f}"

        pct_b = indicators.get("bb_pct_b", 0.5)
        if pct_b >= 1.0:
            interp["bb_summary"] = "Price above upper BB — extended / overbought"
        elif pct_b <= 0.0:
            interp["bb_summary"] = "Price below lower BB — extended / oversold"
        else:
            interp["bb_summary"] = f"Price at {pct_b:.0%} within Bollinger Bands"

        crossover = indicators.get("ema_crossover", "none")
        interp["ema_summary"] = f"EMA crossover: {crossover.replace('_', ' ')}"

        vol_ratio = indicators.get("volume_ratio", 1.0)
        if vol_ratio >= 2.0:
            interp["volume_summary"] = f"High volume ({vol_ratio:.1f}x avg) — strong conviction"
        elif vol_ratio <= 0.5:
            interp["volume_summary"] = f"Low volume ({vol_ratio:.1f}x avg) — weak signal"
        else:
            interp["volume_summary"] = f"Normal volume ({vol_ratio:.1f}x avg)"

        return interp
