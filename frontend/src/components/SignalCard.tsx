"use client";
import Link from "next/link";
import type { Signal } from "@/lib/types";
import { formatDistanceToNow } from "date-fns";

interface Props {
  signal: Signal;
}

const SIGNAL_COLOR = {
  BUY: "border-green-500 bg-green-500/5",
  SELL: "border-red-500 bg-red-500/5",
  HOLD: "border-gray-500 bg-gray-500/5",
};

const SIGNAL_BADGE = {
  BUY: "bg-green-500/20 text-green-400 border border-green-500/40",
  SELL: "bg-red-500/20 text-red-400 border border-red-500/40",
  HOLD: "bg-gray-500/20 text-gray-400 border border-gray-500/40",
};

const SIGNAL_EMOJI = { BUY: "🟢", SELL: "🔴", HOLD: "⚪" };

const TIMEFRAME_COLOR = {
  short: "text-yellow-400",
  mid: "text-blue-400",
  long: "text-purple-400",
};

export default function SignalCard({ signal }: Props) {
  const sig = signal.signal;
  const conf = signal.confidence ?? 0;
  const timeAgo = signal.created_at
    ? formatDistanceToNow(new Date(signal.created_at), { addSuffix: true })
    : "";

  return (
    <Link href={`/signals/${signal.ticker}`}>
      <div
        className={`rounded-xl border-2 p-4 cursor-pointer hover:scale-[1.02] transition-all duration-200 ${SIGNAL_COLOR[sig]}`}
        style={{ backgroundColor: "rgba(26, 29, 46, 0.9)" }}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold text-white">{signal.ticker}</span>
              <span
                className={`text-xs px-2 py-0.5 rounded-full font-semibold ${SIGNAL_BADGE[sig]}`}
              >
                {SIGNAL_EMOJI[sig]} {sig}
              </span>
            </div>
            <div className="text-xs text-gray-400 mt-0.5">
              {signal.exchange} · {signal.asset_type?.toUpperCase()}
            </div>
          </div>
          {/* Confidence ring */}
          <div className="flex flex-col items-center">
            <div
              className={`text-2xl font-bold ${
                conf >= 75 ? "text-green-400" : conf >= 50 ? "text-yellow-400" : "text-gray-400"
              }`}
            >
              {conf}%
            </div>
            <div className="text-xs text-gray-500">confidence</div>
          </div>
        </div>

        {/* Prices */}
        {sig !== "HOLD" && (
          <div className="grid grid-cols-3 gap-2 mb-3 text-center">
            <div className="bg-white/5 rounded-lg p-2">
              <div className="text-xs text-gray-500">Entry</div>
              <div className="text-sm font-mono text-white">
                {signal.entry_price?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
              </div>
            </div>
            <div className="bg-green-500/10 rounded-lg p-2">
              <div className="text-xs text-gray-500">Target</div>
              <div className="text-sm font-mono text-green-400">
                {signal.target_price?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
              </div>
            </div>
            <div className="bg-red-500/10 rounded-lg p-2">
              <div className="text-xs text-gray-500">Stop</div>
              <div className="text-sm font-mono text-red-400">
                {signal.stop_loss?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
              </div>
            </div>
          </div>
        )}

        {/* R:R + timeframe */}
        <div className="flex items-center gap-3 mb-3 text-xs">
          {signal.risk_reward_ratio && (
            <span className="text-blue-400 font-semibold">
              R:R {signal.risk_reward_ratio}x
            </span>
          )}
          {signal.timeframe && (
            <span className={`font-medium ${TIMEFRAME_COLOR[signal.timeframe] ?? "text-gray-400"}`}>
              {signal.timeframe.toUpperCase()} TERM
            </span>
          )}
        </div>

        {/* Reasoning */}
        {signal.reasoning && (
          <p className="text-xs text-gray-400 line-clamp-2 mb-3">{signal.reasoning}</p>
        )}

        {/* Risks + timestamp */}
        <div className="flex items-center justify-between">
          <div className="flex flex-wrap gap-1">
            {(signal.key_risks ?? []).slice(0, 2).map((risk, i) => (
              <span
                key={i}
                className="text-[10px] bg-orange-500/10 text-orange-400 border border-orange-500/20 rounded px-1.5 py-0.5"
              >
                ⚠️ {risk.length > 25 ? risk.slice(0, 25) + "…" : risk}
              </span>
            ))}
          </div>
          <span className="text-[10px] text-gray-600">{timeAgo}</span>
        </div>
      </div>
    </Link>
  );
}
