#!/bin/bash
# One-time setup script for the AI Trading Signal Agent

set -e

echo "🚀 Setting up AI Trading Signal Agent..."
echo ""

# ── Backend ─────────────────────────────────────────────────────────────────
echo "📦 Setting up Python backend..."
cd "$(dirname "$0")/backend"

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "⚠️  Created backend/.env — EDIT IT with your API keys before starting!"
fi

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt

echo "✅ Backend dependencies installed"

# ── Frontend ─────────────────────────────────────────────────────────────────
echo ""
echo "📦 Setting up Next.js frontend..."
cd "../frontend"
npm install --legacy-peer-deps

echo "✅ Frontend dependencies installed"

echo ""
echo "══════════════════════════════════════════════════════"
echo "✅ Setup complete!"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Edit backend/.env with your API keys:"
echo "   - ANTHROPIC_API_KEY  (required — get from console.anthropic.com)"
echo "   - TELEGRAM_BOT_TOKEN (optional — from @BotFather)"
echo "   - TELEGRAM_CHAT_ID   (optional — your chat ID)"
echo "   - NEWSAPI_KEY        (optional — from newsapi.org)"
echo ""
echo "2. Test with one signal (in backend/):"
echo "   source .venv/bin/activate"
echo "   python run_signal.py AAPL"
echo ""
echo "3. Start the API server (in backend/):"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""
echo "4. Start the dashboard (in frontend/):"
echo "   npm run dev"
echo "   → Open http://localhost:3000"
echo "══════════════════════════════════════════════════════"
