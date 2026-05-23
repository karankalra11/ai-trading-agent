"use client";
import { useState } from "react";
import { useSignals } from "@/hooks/useSignals";
import SignalCard from "@/components/SignalCard";
import MarketFilter, { TABS } from "@/components/MarketFilter";
import type { Signal } from "@/lib/types";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("");
  const [signalFilter, setSignalFilter] = useState<string>("");

  const tabConfig = TABS.find((t) => t.key === activeTab);

  const { signals, loading, error, lastUpdated, refetch } = useSignals({
    // @ts-expect-error dynamic tab config
    asset_type: tabConfig?.assetType,
    // @ts-expect-error dynamic tab config
    exchange: tabConfig?.exchange,
    signal_type: signalFilter || undefined,
  });

  const buyCount = signals.filter((s) => s.signal === "BUY").length;
  const sellCount = signals.filter((s) => s.signal === "SELL").length;
  const holdCount = signals.filter((s) => s.signal === "HOLD").length;

  return (
    <div>
      {/* Stats bar */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: "BUY Signals", count: buyCount, color: "text-green-400", bg: "bg-green-500/10 border-green-500/20" },
          { label: "SELL Signals", count: sellCount, color: "text-red-400", bg: "bg-red-500/10 border-red-500/20" },
          { label: "HOLD Signals", count: holdCount, color: "text-gray-400", bg: "bg-gray-500/10 border-gray-500/20" },
        ].map((stat) => (
          <div key={stat.label} className={`rounded-xl border p-4 ${stat.bg}`}>
            <div className={`text-3xl font-bold ${stat.color}`}>{stat.count}</div>
            <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <MarketFilter active={activeTab} onChange={setActiveTab} />

        <div className="flex gap-2">
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
              {sig || "All Signals"}
            </button>
          ))}
        </div>
      </div>

      {/* Last updated + refresh */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">
          {signals.length} Signal{signals.length !== 1 ? "s" : ""}
        </h2>
        <div className="flex items-center gap-3 text-xs text-gray-500">
          {lastUpdated && (
            <span>Updated {lastUpdated.toLocaleTimeString()}</span>
          )}
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
            <div
              key={i}
              className="h-52 rounded-xl bg-white/5 animate-pulse border border-white/10"
            />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-20">
          <div className="text-4xl mb-3">⚠️</div>
          <p className="text-gray-400">{error}</p>
          <p className="text-gray-600 text-sm mt-2">
            Make sure the backend is running on port 8000
          </p>
          <button
            onClick={refetch}
            className="mt-4 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm"
          >
            Retry
          </button>
        </div>
      ) : signals.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-4xl mb-3">🔍</div>
          <p className="text-gray-400">No signals yet</p>
          <p className="text-gray-600 text-sm mt-2">
            Run{" "}
            <code className="bg-white/10 px-1.5 py-0.5 rounded text-xs">
              python run_signal.py AAPL
            </code>{" "}
            in the backend to generate your first signal
          </p>
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
