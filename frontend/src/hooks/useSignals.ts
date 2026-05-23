"use client";
import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import type { Signal } from "@/lib/types";

interface UseSignalsOptions {
  exchange?: string;
  asset_type?: string;
  signal_type?: string;
  min_confidence?: number;
  pollIntervalMs?: number;
}

export function useSignals(options: UseSignalsOptions = {}) {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const { pollIntervalMs = 60_000 } = options;

  const fetch = useCallback(async () => {
    try {
      const data = await api.signals.list({
        exchange: options.exchange,
        asset_type: options.asset_type,
        signal_type: options.signal_type,
        min_confidence: options.min_confidence,
      });
      setSignals(data);
      setLastUpdated(new Date());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to fetch signals");
    } finally {
      setLoading(false);
    }
  }, [options.exchange, options.asset_type, options.signal_type, options.min_confidence]);

  useEffect(() => {
    fetch();
    const id = setInterval(fetch, pollIntervalMs);
    return () => clearInterval(id);
  }, [fetch, pollIntervalMs]);

  return { signals, loading, error, lastUpdated, refetch: fetch };
}
