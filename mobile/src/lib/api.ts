import { API_BASE_URL } from "./config";
import type { Signal, SentimentPoint } from "./types";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json();
}

export const api = {
  signals: {
    list: (params?: {
      asset_type?: string;
      signal_type?: string;
      min_confidence?: number;
    }) => {
      const qs = new URLSearchParams();
      if (params?.asset_type) qs.set("asset_type", params.asset_type);
      if (params?.signal_type) qs.set("signal_type", params.signal_type);
      if (params?.min_confidence != null)
        qs.set("min_confidence", String(params.min_confidence));
      return fetchJSON<Signal[]>(`/api/signals?${qs.toString()}`);
    },
    latest: (ticker: string) =>
      fetchJSON<Signal>(`/api/signals/${ticker}/latest`),
    history: (ticker: string, limit = 15) =>
      fetchJSON<Signal[]>(`/api/signals/${ticker}?limit=${limit}`),
    stats: () =>
      fetchJSON<{ total: number; buy: number; sell: number; hold: number }>(
        "/api/signals/stats"
      ),
    trigger: (ticker: string, market = "us") =>
      fetch(
        `${API_BASE_URL}/api/signals/trigger?ticker=${ticker}&market=${market}`,
        { method: "POST" }
      ),
  },
  news: {
    sentimentHistory: (ticker: string) =>
      fetchJSON<SentimentPoint[]>(`/api/news/${ticker}/sentiment-history`),
  },
  health: () => fetchJSON<{ status: string }>("/health"),
};
