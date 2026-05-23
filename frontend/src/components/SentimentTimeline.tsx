"use client";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import type { SentimentPoint } from "@/lib/types";
import { format } from "date-fns";

interface Props {
  data: SentimentPoint[];
  ticker: string;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const score = payload[0].value;
    const sig = payload[0].payload.signal;
    const conf = payload[0].payload.confidence;
    return (
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 text-xs shadow-xl">
        <p className="text-gray-400 mb-1">{label}</p>
        <p className={`font-bold ${score > 0 ? "text-green-400" : score < 0 ? "text-red-400" : "text-gray-400"}`}>
          Score: {score > 0 ? "+" : ""}{score.toFixed(4)}
        </p>
        <p className="text-gray-300">Signal: {sig} ({conf}%)</p>
      </div>
    );
  }
  return null;
};

export default function SentimentTimeline({ data, ticker }: Props) {
  const formatted = data.map((d) => ({
    ...d,
    time: d.timestamp ? format(new Date(d.timestamp), "MMM d HH:mm") : "",
    score: d.score,
  }));

  if (formatted.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-gray-500 text-sm">
        No sentiment history yet for {ticker}
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={180}>
      <AreaChart data={formatted} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="sentimentGradientPos" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="sentimentGradientNeg" x1="0" y1="1" x2="0" y2="0">
            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#2d3148" />
        <XAxis dataKey="time" tick={{ fill: "#6b7280", fontSize: 10 }} />
        <YAxis domain={[-1, 1]} tick={{ fill: "#6b7280", fontSize: 10 }} />
        <Tooltip content={<CustomTooltip />} />
        <ReferenceLine y={0} stroke="#4b5563" strokeDasharray="4 4" />
        <Area
          type="monotone"
          dataKey="score"
          stroke="#818cf8"
          strokeWidth={2}
          fill="url(#sentimentGradientPos)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
