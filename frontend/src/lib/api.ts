import type { Signal, OHLCVBar, SentimentPoint, SignalStats } from "./types";

const BASE = "/api";

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error ${res.status}: ${url}`);
  return res.json();
}

export const api = {
  signals: {
    list: (params?: {
      exchange?: string;
      asset_type?: string;
      signal_type?: string;
      min_confidence?: number;
    }) => {
      const qs = new URLSearchParams();
      if (params?.exchange) qs.set("exchange", params.exchange);
      if (params?.asset_type) qs.set("asset_type", params.asset_type);
      if (params?.signal_type) qs.set("signal_type", params.signal_type);
      if (params?.min_confidence != null)
        qs.set("min_confidence", String(params.min_confidence));
      return fetchJSON<Signal[]>(`${BASE}/signals?${qs.toString()}`);
    },
    latest: (ticker: string) =>
      fetchJSON<Signal>(`${BASE}/signals/${ticker}/latest`),
    history: (ticker: string, limit = 20) =>
      fetchJSON<Signal[]>(`${BASE}/signals/${ticker}?limit=${limit}`),
    stats: () => fetchJSON<SignalStats>(`${BASE}/signals/stats`),
    trigger: (ticker: string, market = "us") =>
      fetch(`${BASE}/signals/trigger?ticker=${ticker}&market=${market}`, {
        method: "POST",
      }),
  },
  market: {
    watchlist: () =>
      fetchJSON<Record<string, string[]>>(`${BASE}/market/watchlist`),
    ohlcv: (ticker: string, period = "5d", interval = "30m") =>
      fetchJSON<OHLCVBar[]>(
        `${BASE}/market/${ticker}/ohlcv?period=${period}&interval=${interval}`
      ),
    indicators: (ticker: string) =>
      fetchJSON<Record<string, unknown>>(`${BASE}/market/${ticker}/indicators`),
  },
  news: {
    list: (ticker: string) =>
      fetchJSON<unknown[]>(`${BASE}/news/${ticker}`),
    sentimentHistory: (ticker: string) =>
      fetchJSON<SentimentPoint[]>(`${BASE}/news/${ticker}/sentiment-history`),
  },
};
