"use client";

const TABS = [
  { key: "", label: "🌍 All" },
  { key: "stock_us", label: "🇺🇸 US Stocks", assetType: "stock", exchange: "NASDAQ/NYSE" },
  { key: "stock_india", label: "🇮🇳 India", assetType: "stock", exchange: "NSE/BSE" },
  { key: "crypto", label: "₿ Crypto", assetType: "crypto" },
  { key: "etf", label: "📦 ETFs", assetType: "etf" },
];

interface Props {
  active: string;
  onChange: (key: string) => void;
}

export default function MarketFilter({ active, onChange }: Props) {
  return (
    <div className="flex gap-2 flex-wrap">
      {TABS.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
            active === tab.key
              ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/30"
              : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

export { TABS };
