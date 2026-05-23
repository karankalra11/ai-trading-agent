"use client";
import { use, useEffect, useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";
import { useOHLCV, useSentimentHistory } from "@/hooks/useMarketData";
import type { Signal } from "@/lib/types";
import { formatDistanceToNow } from "date-fns";

const CandlestickChart = dynamic(() => import("@/components/CandlestickChart"), { ssr: false });
const SentimentTimeline = dynamic(() => import("@/components/SentimentTimeline"), { ssr: false });

const SIGNAL_COLOR: Record<string, string> = {
  BUY: "text-green-400 bg-green-500/10 border-green-500/30",
  SELL: "text-red-400 bg-red-500/10 border-red-500/30",
  HOLD: "text-gray-400 bg-gray-500/10 border-gray-500/30",
};

export default function TickerPage({ params }: { params: Promise<{ ticker: string }> }) {
  const { ticker } = use(params);
  const [latestSignal, setLatestSignal] = useState<Signal | null>(null);
  const [history, setHistory] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState("5d");
  const [interval, setInterval] = useState("30m");

  const { data: ohlcv } = useOHLCV(ticker, period, interval);
  const { data: sentimentData } = useSentimentHistory(ticker);

  useEffect(() => {
    async function load() {
      try {
        const [sig, hist] = await Promise.all([
          api.signals.latest(ticker).catch(() => null),
          api.signals.history(ticker, 20),
        ]);
        setLatestSignal(sig);
        setHistory(hist);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [ticker]);

  const sig = latestSignal?.signal ?? "HOLD";

  return (
    <div>
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
        <Link href="/" className="hover:text-white transition-colors">
          ← Dashboard
        </Link>
        <span>/</span>
        <span className="text-white">{ticker}</span>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 rounded-xl bg-white/5 animate-pulse" />
          ))}
        </div>
      ) : (
        <>
          {/* Signal header */}
          {latestSignal ? (
            <div className={`rounded-xl border-2 p-6 mb-6 ${SIGNAL_COLOR[sig]?.split(" ").slice(1).join(" ") ?? ""}`}>
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h1 className="text-3xl font-bold text-white">{ticker}</h1>
                    <span className={`px-3 py-1 rounded-full text-sm font-bold border ${SIGNAL_COLOR[sig]}`}>
                      {sig}
                    </span>
                  </div>
                  <p className="text-gray-400 text-sm">
                    {latestSignal.exchange} · {latestSignal.asset_type?.toUpperCase()} ·{" "}
                    {latestSignal.created_at
                      ? formatDistanceToNow(new Date(latestSignal.created_at), { addSuffix: true })
                      : ""}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-5xl font-bold text-white">{latestSignal.confidence}%</div>
                  <div className="text-gray-500 text-sm">confidence</div>
                </div>
              </div>

              {/* Price levels */}
              {sig !== "HOLD" && (
                <div className="grid grid-cols-3 gap-4 mt-5">
                  {[
                    { label: "Entry", value: latestSignal.entry_price, color: "text-indigo-400" },
                    { label: "Target", value: latestSignal.target_price, color: "text-green-400" },
                    { label: "Stop Loss", value: latestSignal.stop_loss, color: "text-red-400" },
                  ].map((p) => (
                    <div key={p.label} className="bg-white/5 rounded-xl p-4 text-center">
                      <div className="text-xs text-gray-500 mb-1">{p.label}</div>
                      <div className={`text-xl font-mono font-bold ${p.color}`}>
                        {p.value?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Meta */}
              <div className="flex flex-wrap gap-4 mt-4 text-sm text-gray-400">
                {latestSignal.risk_reward_ratio && (
                  <span className="text-blue-400">⚖️ R:R {latestSignal.risk_reward_ratio}x</span>
                )}
                {latestSignal.timeframe && (
                  <span>⏱️ {latestSignal.timeframe.toUpperCase()} TERM</span>
                )}
                {(latestSignal.data_sources ?? []).map((s) => (
                  <span key={s} className="bg-white/5 px-2 py-0.5 rounded text-xs">
                    {s}
                  </span>
                ))}
              </div>

              {/* Reasoning */}
              {latestSignal.reasoning && (
                <p className="mt-4 text-gray-300 text-sm leading-relaxed bg-white/5 rounded-xl p-4">
                  💬 {latestSignal.reasoning}
                </p>
              )}

              {/* Key risks */}
              {(latestSignal.key_risks ?? []).length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {(latestSignal.key_risks ?? []).map((risk, i) => (
                    <span
                      key={i}
                      className="text-xs bg-orange-500/10 text-orange-400 border border-orange-500/20 rounded-full px-3 py-1"
                    >
                      ⚠️ {risk}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-gray-400 mb-6 p-6 bg-white/5 rounded-xl">
              No signals found for {ticker} yet. Run{" "}
              <code className="bg-white/10 px-1.5 py-0.5 rounded">
                python run_signal.py {ticker}
              </code>
            </div>
          )}

          {/* Chart */}
          <div className="bg-[#1a1d2e] rounded-xl border border-white/10 p-4 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-white">Price Chart</h2>
              <div className="flex gap-2">
                {[
                  { period: "1d", interval: "5m", label: "1D" },
                  { period: "5d", interval: "30m", label: "5D" },
                  { period: "1mo", interval: "1d", label: "1M" },
                ].map((opt) => (
                  <button
                    key={opt.label}
                    onClick={() => { setPeriod(opt.period); setInterval(opt.interval); }}
                    className={`text-xs px-2.5 py-1 rounded-lg transition-all ${
                      period === opt.period
                        ? "bg-indigo-600 text-white"
                        : "bg-white/5 text-gray-400 hover:bg-white/10"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
            <CandlestickChart data={ohlcv} signal={latestSignal} />
          </div>

          {/* Sentiment timeline */}
          {sentimentData.length > 0 && (
            <div className="bg-[#1a1d2e] rounded-xl border border-white/10 p-4 mb-6">
              <h2 className="font-semibold text-white mb-4">Signal Sentiment History</h2>
              <SentimentTimeline data={sentimentData} ticker={ticker} />
            </div>
          )}

          {/* Signal history table */}
          {history.length > 0 && (
            <div className="bg-[#1a1d2e] rounded-xl border border-white/10 p-4">
              <h2 className="font-semibold text-white mb-4">Signal History</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-gray-500 border-b border-white/10">
                      <th className="pb-3 text-left">Time</th>
                      <th className="pb-3 text-left">Signal</th>
                      <th className="pb-3 text-right">Entry</th>
                      <th className="pb-3 text-right">Target</th>
                      <th className="pb-3 text-right">Stop</th>
                      <th className="pb-3 text-right">Confidence</th>
                      <th className="pb-3 text-left">Timeframe</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {history.map((s) => (
                      <tr key={s.id} className="hover:bg-white/5 transition-colors">
                        <td className="py-3 text-gray-500 text-xs">
                          {s.created_at
                            ? new Date(s.created_at).toLocaleString()
                            : "—"}
                        </td>
                        <td className="py-3">
                          <span className={`text-xs font-bold px-2 py-0.5 rounded border ${SIGNAL_COLOR[s.signal]}`}>
                            {s.signal}
                          </span>
                        </td>
                        <td className="py-3 text-right font-mono text-gray-300">
                          {s.entry_price?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
                        </td>
                        <td className="py-3 text-right font-mono text-green-400">
                          {s.target_price?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
                        </td>
                        <td className="py-3 text-right font-mono text-red-400">
                          {s.stop_loss?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
                        </td>
                        <td className="py-3 text-right text-indigo-400 font-medium">
                          {s.confidence}%
                        </td>
                        <td className="py-3 text-gray-500 text-xs uppercase">
                          {s.timeframe ?? "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
