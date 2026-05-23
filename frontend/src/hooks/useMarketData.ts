"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { OHLCVBar, SentimentPoint } from "@/lib/types";

export function useOHLCV(ticker: string, period = "5d", interval = "30m") {
  const [data, setData] = useState<OHLCVBar[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!ticker) return;
    setLoading(true);
    api.market
      .ohlcv(ticker, period, interval)
      .then(setData)
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [ticker, period, interval]);

  return { data, loading };
}

export function useSentimentHistory(ticker: string) {
  const [data, setData] = useState<SentimentPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!ticker) return;
    api.news
      .sentimentHistory(ticker)
      .then(setData)
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [ticker]);

  return { data, loading };
}
