export type SignalType = "BUY" | "SELL" | "HOLD";
export type AssetType = "stock" | "crypto" | "etf";
export type Timeframe = "short" | "mid" | "long";

export interface Signal {
  id: number;
  ticker: string;
  exchange: string;
  asset_type: AssetType;
  signal: SignalType;
  entry_price: number | null;
  target_price: number | null;
  stop_loss: number | null;
  confidence: number | null;
  reasoning: string | null;
  timeframe: Timeframe | null;
  data_sources: string[] | null;
  risk_reward_ratio: number | null;
  key_risks: string[] | null;
  created_at: string;
}

export interface OHLCVBar {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface SentimentPoint {
  timestamp: string;
  score: number;
  signal: SignalType;
  confidence: number | null;
}

export interface SignalStats {
  total: number;
  buy: number;
  sell: number;
  hold: number;
}
