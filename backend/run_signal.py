#!/usr/bin/env python3
"""
Quick CLI runner — generates a signal for a single ticker without starting the API.

Usage:
  cd backend
  python run_signal.py AAPL
  python run_signal.py BTC --market crypto
  python run_signal.py RELIANCE.NS --market india
"""
import sys
import json
import argparse
from dotenv import load_dotenv

load_dotenv()

from app.database import init_db
from app.signals.signal_runner import SignalRunner


def main():
    parser = argparse.ArgumentParser(description="Run a trading signal for a single ticker")
    parser.add_argument("ticker", help="Ticker symbol e.g. AAPL, BTC, RELIANCE.NS")
    parser.add_argument("--market", default="us", choices=["us", "india", "crypto", "etf"],
                        help="Market type (default: us)")
    args = parser.parse_args()

    init_db()
    runner = SignalRunner()
    result = runner.run_for_ticker(args.ticker.upper(), args.market)

    if result:
        print("\n" + "=" * 60)
        print("📊 SIGNAL RESULT")
        print("=" * 60)
        clean = {k: v for k, v in result.items() if k != "raw_claude_response"}
        print(json.dumps(clean, indent=2))
    else:
        print(f"\n❌ No signal generated for {args.ticker}")
        sys.exit(1)


if __name__ == "__main__":
    main()
