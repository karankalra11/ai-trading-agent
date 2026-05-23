import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Trading Signal Agent",
  description: "Real-time BUY/SELL/HOLD signals powered by Claude AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0f1117] text-gray-100 antialiased">
        <nav className="border-b border-white/10 px-6 py-3 flex items-center justify-between sticky top-0 bg-[#0f1117]/80 backdrop-blur z-50">
          <div className="flex items-center gap-3">
            <span className="text-xl">📈</span>
            <span className="font-bold text-white text-lg">AI Trading Agent</span>
            <span className="text-xs bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full">
              BETA
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-400">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              Live
            </span>
            <a href="/" className="hover:text-white transition-colors">Dashboard</a>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
          {children}
        </main>
      </body>
    </html>
  );
}
