"use client";
import { useEffect, useRef } from "react";
import type { OHLCVBar, Signal } from "@/lib/types";

interface Props {
  data: OHLCVBar[];
  signal?: Signal | null;
}

export default function CandlestickChart({ data, signal }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const chartRef = useRef<any>(null);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;

    // Dynamically import lightweight-charts (client only)
    import("lightweight-charts").then(({ createChart, ColorType, LineStyle }) => {
      // Cleanup previous chart
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }

      const chart = createChart(containerRef.current!, {
        layout: {
          background: { type: ColorType.Solid, color: "transparent" },
          textColor: "#9ca3af",
        },
        grid: {
          vertLines: { color: "#2d3148" },
          horzLines: { color: "#2d3148" },
        },
        crosshair: { mode: 1 },
        rightPriceScale: { borderColor: "#2d3148" },
        timeScale: { borderColor: "#2d3148", timeVisible: true },
        width: containerRef.current!.clientWidth,
        height: 320,
      });
      chartRef.current = chart;

      const candleSeries = chart.addCandlestickSeries({
        upColor: "#22c55e",
        downColor: "#ef4444",
        borderUpColor: "#22c55e",
        borderDownColor: "#ef4444",
        wickUpColor: "#22c55e",
        wickDownColor: "#ef4444",
      });
      candleSeries.setData(data as Parameters<typeof candleSeries.setData>[0]);

      // Add signal price lines
      if (signal && signal.signal !== "HOLD") {
        if (signal.entry_price) {
          candleSeries.createPriceLine({
            price: signal.entry_price,
            color: "#818cf8",
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            axisLabelVisible: true,
            title: "Entry",
          });
        }
        if (signal.target_price) {
          candleSeries.createPriceLine({
            price: signal.target_price,
            color: "#22c55e",
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            axisLabelVisible: true,
            title: "Target",
          });
        }
        if (signal.stop_loss) {
          candleSeries.createPriceLine({
            price: signal.stop_loss,
            color: "#ef4444",
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            axisLabelVisible: true,
            title: "Stop",
          });
        }
      }

      chart.timeScale().fitContent();

      const handleResize = () => {
        if (containerRef.current) {
          chart.applyOptions({ width: containerRef.current.clientWidth });
        }
      };
      window.addEventListener("resize", handleResize);
      return () => window.removeEventListener("resize", handleResize);
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [data, signal]);

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[320px] text-gray-500 text-sm">
        No chart data available
      </div>
    );
  }

  return <div ref={containerRef} className="w-full" />;
}
