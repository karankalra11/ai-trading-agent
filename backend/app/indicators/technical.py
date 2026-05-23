import pandas as pd
import pandas_ta as ta
import numpy as np


class TechnicalAnalyzer:

    def compute_all(self, df: pd.DataFrame) -> dict:
        """Compute all technical indicators and return a flat dict."""
        if df.empty or len(df) < 20:
            return {}

        result = {}
        try:
            result.update(self.compute_rsi(df))
        except Exception:
            pass
        try:
            result.update(self.compute_macd(df))
        except Exception:
            pass
        try:
            result.update(self.compute_bollinger(df))
        except Exception:
            pass
        try:
            result.update(self.compute_ema(df))
        except Exception:
            pass
        try:
            result.update(self.compute_volume(df))
        except Exception:
            pass
        try:
            result.update(self.compute_atr(df))
        except Exception:
            pass

        result["interpretations"] = self.interpret_signals(result)
        return result

    def compute_rsi(self, df: pd.DataFrame, length: int = 14) -> dict:
        rsi = ta.rsi(df["close"], length=length)
        val = float(rsi.iloc[-1]) if rsi is not None and not rsi.empty else 50.0
        if val >= 70:
            signal = "overbought"
        elif val <= 30:
            signal = "oversold"
        else:
            signal = "neutral"
        return {"rsi_14": round(val, 2), "rsi_signal": signal}

    def compute_macd(self, df: pd.DataFrame) -> dict:
        macd_df = ta.macd(df["close"], fast=12, slow=26, signal=9)
        if macd_df is None or macd_df.empty:
            return {"macd": 0, "macd_signal_line": 0, "macd_histogram": 0, "macd_trend": "neutral"}
        macd_val = float(macd_df.iloc[-1, 0])
        signal_val = float(macd_df.iloc[-1, 1])
        hist_val = float(macd_df.iloc[-1, 2])
        trend = "bullish" if macd_val > signal_val else "bearish"
        return {
            "macd": round(macd_val, 4),
            "macd_signal_line": round(signal_val, 4),
            "macd_histogram": round(hist_val, 4),
            "macd_trend": trend,
        }

    def compute_bollinger(self, df: pd.DataFrame, length: int = 20, std: float = 2.0) -> dict:
        bb = ta.bbands(df["close"], length=length, std=std)
        if bb is None or bb.empty:
            return {}
        upper = float(bb.iloc[-1, 0])
        mid = float(bb.iloc[-1, 1])
        lower = float(bb.iloc[-1, 2])
        bw = float(bb.iloc[-1, 3]) if bb.shape[1] > 3 else 0.0
        pct_b = float(bb.iloc[-1, 4]) if bb.shape[1] > 4 else 0.5
        return {
            "bb_upper": round(upper, 4),
            "bb_middle": round(mid, 4),
            "bb_lower": round(lower, 4),
            "bb_bandwidth": round(bw, 4),
            "bb_pct_b": round(pct_b, 4),
        }

    def compute_ema(self, df: pd.DataFrame) -> dict:
        ema20 = ta.ema(df["close"], length=20)
        ema50 = ta.ema(df["close"], length=50)
        e20 = float(ema20.iloc[-1]) if ema20 is not None and not ema20.empty else 0
        e50 = float(ema50.iloc[-1]) if ema50 is not None and not ema50.empty else 0

        crossover = "none"
        if len(df) >= 51 and ema20 is not None and ema50 is not None:
            prev_e20 = float(ema20.iloc[-2]) if len(ema20) >= 2 else e20
            prev_e50 = float(ema50.iloc[-2]) if len(ema50) >= 2 else e50
            if prev_e20 <= prev_e50 and e20 > e50:
                crossover = "golden_cross"
            elif prev_e20 >= prev_e50 and e20 < e50:
                crossover = "death_cross"
            elif e20 > e50:
                crossover = "above"
            else:
                crossover = "below"

        return {"ema_20": round(e20, 4), "ema_50": round(e50, 4), "ema_crossover": crossover}

    def compute_volume(self, df: pd.DataFrame) -> dict:
        if "volume" not in df.columns or df["volume"].sum() == 0:
            return {"avg_volume_10d": 0, "current_volume": 0, "volume_ratio": 1.0}
        avg_vol = float(df["volume"].tail(10).mean())
        curr_vol = float(df["volume"].iloc[-1])
        ratio = round(curr_vol / avg_vol, 2) if avg_vol > 0 else 1.0
        return {"avg_volume_10d": int(avg_vol), "current_volume": int(curr_vol), "volume_ratio": ratio}

    def compute_atr(self, df: pd.DataFrame, length: int = 14) -> dict:
        atr = ta.atr(df["high"], df["low"], df["close"], length=length)
        val = float(atr.iloc[-1]) if atr is not None and not atr.empty else 0.0
        return {"atr_14": round(val, 4)}

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
