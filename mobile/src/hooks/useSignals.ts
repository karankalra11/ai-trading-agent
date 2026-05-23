import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import type { Signal } from "@/lib/types";

interface Options {
  asset_type?: string;
  signal_type?: string;
  min_confidence?: number;
  pollMs?: number;
}

export function useSignals(opts: Options = {}) {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const { pollMs = 60_000 } = opts;

  const load = useCallback(async () => {
    try {
      const data = await api.signals.list({
        asset_type: opts.asset_type,
        signal_type: opts.signal_type,
        min_confidence: opts.min_confidence,
      });
      setSignals(data);
      setLastUpdated(new Date());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }, [opts.asset_type, opts.signal_type, opts.min_confidence]);

  useEffect(() => {
    load();
    const id = setInterval(load, pollMs);
    return () => clearInterval(id);
  }, [load, pollMs]);

  return { signals, loading, error, lastUpdated, refetch: load };
}
