"use client";
import { useState, useEffect } from "react";
import { useSignals } from "@/hooks/useSignals";
import SignalCard from "@/components/SignalCard";
import MarketFilter, { TABS } from "@/components/MarketFilter";
import type { Signal } from "@/lib/types";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("");
  const [signalFilter, setSignalFilter] = useState<string>("");
  const [generating, setGenerating] = useState(false);
  const [generateMsg, setGenerateMsg] = useState("");
  const [serverAwake, setServerAwake] = useState<boolean | null>(null);

  const tabConfig = TABS.find((t) => t.key === activeTab);

  const { signals, loading, error, lastUpdated, refetch } = useSignals({
    // @ts-expect-error dynamic tab config
    asset_type: tabConfig?.assetType,
    // @ts-expect-error dynamic tab config
    exchange: tabConfig?.exchange,
    signal_type: signalFilter || undefined,
    pollIntervalMs: 30_000,   // poll every 30s for freshness
  });

  // Check if server is awake on mount
  useEffect(() => {
    fetch("/api/../health")
      .then((r) => r.ok ? setServerAwake(true) : setServerAwake(false))
      .catch(() => setServerAwake(false));
  }, []);

  const handleGenerateAll = async () => {
    setGenerating(true);
    setGenerateMsg("Waking up server…");
    try {
      const res = await fetch("/api/signals/run-all");
      if (res.ok) {
        setGenerateMsg("✅ Generating signals for all tickers… (~2 min)");
        // Poll every 10s for new signals while generating
        let polls = 0;
        const interval = setInterval(async () => {
          polls++;
          await refetch();
          if (polls >= 12) {   // stop after 2 min
            clearInterval(interval);
            setGenerating(false);
            setGenerateMsg("");
          }
        }, 10_000);
      } else {
        setGenerateMsg("❌ Server error — try again");
        setGenerating(false);
      }
    } catch {
      setGenerateMsg("❌ Cannot reach server");
      setGenerating(false);
    }
  };

  const buyCount = signals.filter((s) => s.signal === "BUY").length;
  const sellCount = signals.filter((s) => s.signal === "SELL").length;
  const holdCount = signals.filter((s) => s.signal === "HOLD").length;

  return (
    <div>
      {/* Server wake-up banner */}
      {serverAwake === false && (
        <div className="mb-4 bg-yellow-500/10 border border-yellow-500/30 rounded-xl px-4 py-3 text-yellow-300 text-sm flex items-center gap-2">
          <span className="animate-spin">⏳</span>
          Server is waking up (free tier sleeps after 15 min) — may take 30 seconds…
        </div>
      )}

      {/* Stats bar */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: "BUY", count: buyCount, color: "text-green-400", bg: "bg-green-500/10 border-green-500/20" },
          { label: "SELL", count: sellCount, color: "text-red-400", bg: "bg-red-500/10 border-red-500/20" },
          { label: "HOLD", count: holdCount, color: "text-gray-400", bg: "bg-gray-500/10 border-gray-500/20" },
        ].map((stat) => (
          <div key={stat.label} className={`rounded-xl border p-4 ${stat.bg}`}>
            <div className={`text-3xl font-bold ${stat.color}`}>{stat.count}</div>
            <div className="text-sm text-gray-500 mt-1">{stat.label} Signals</div>
          </div>
        ))}
      </div>

      {/* Filters + Generate button */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <MarketFilter active={activeTab} onChange={setActiveTab} />

        <div className="flex gap-2 items-center">
          {["", "BUY", "SELL", "HOLD"].map((sig) => (
            <button
              key={sig}
              onClick={() => setSignalFilter(sig)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                signalFilter === sig
                  ? "bg-indigo-600 text-white"
                  : "bg-white/5 text-gray-400 hover:bg-white/10"
              }`}
            >
              {sig || "All"}
            </button>
          ))}

          <button
            onClick={handleGenerateAll}
            disabled={generating}
            className={`ml-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
              generating
                ? "bg-indigo-600/50 text-indigo-300 cursor-wait"
                : "bg-indigo-600 hover:bg-indigo-500 text-white"
            }`}
          >
            {generating ? (
              <><span className="animate-spin">⚙</span> Generating…</>
            ) : (
              <>⚡ Generate All Signals</>
            )}
          </button>
        </div>
      </div>

      {/* Generate status */}
      {generateMsg && (
        <div className="mb-4 text-sm text-indigo-300 bg-indigo-500/10 border border-indigo-500/20 rounded-lg px-4 py-2">
          {generateMsg}
        </div>
      )}

      {/* Last updated + refresh */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">
          {signals.length} Signal{signals.length !== 1 ? "s" : ""}
        </h2>
        <div className="flex items-center gap-3 text-xs text-gray-500">
          {lastUpdated && <span>Updated {lastUpdated.toLocaleTimeString()}</span>}
          <button
            onClick={refetch}
            className="bg-white/5 hover:bg-white/10 text-gray-300 px-3 py-1.5 rounded-lg transition-all"
          >
            ↻ Refresh
          </button>
        </div>
      </div>

      {/* Signal Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-52 rounded-xl bg-white/5 animate-pulse border border-white/10" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-20">
          <div className="text-4xl mb-3">⚠️</div>
          <p className="text-gray-400 mb-4">Could not reach the backend</p>
          <button onClick={refetch} className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm">
            Retry
          </button>
        </div>
      ) : signals.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">📊</div>
          <p className="text-white font-semibold text-lg mb-2">No signals yet</p>
          <p className="text-gray-500 text-sm mb-6">
            Click the button below to generate AI signals for all tickers
          </p>
          <button
            onClick={handleGenerateAll}
            disabled={generating}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl font-semibold transition-all disabled:opacity-50"
          >
            {generating ? "⚙ Generating… (~2 min)" : "⚡ Generate Signals Now"}
          </button>
          {generateMsg && (
            <p className="mt-4 text-sm text-indigo-300">{generateMsg}</p>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {signals.map((signal: Signal) => (
            <SignalCard key={signal.id} signal={signal} />
          ))}
        </div>
      )}
    </div>
  );
}
