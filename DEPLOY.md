# Deployment Guide

## 1. Host Backend on Render (Free)

### Step 1 — Push to GitHub
```bash
cd ~/trading-signal-agent
git init
git add .
git commit -m "Initial commit — AI Trading Signal Agent"
gh repo create ai-trading-agent --public --source=. --push
# OR: git remote add origin https://github.com/YOUR_USERNAME/ai-trading-agent.git && git push -u origin main
```

### Step 2 — Deploy on Render
1. Go to **https://render.com** → Sign up free
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — it will configure everything
5. Under **Environment Variables**, add:
   - `ANTHROPIC_API_KEY` = your Claude API key
   - `TELEGRAM_BOT_TOKEN` = (optional)
   - `TELEGRAM_CHAT_ID` = (optional)
6. Click **Deploy**

Your backend URL will be: `https://trading-signal-agent-api.onrender.com`

> ⚠️ Free tier spins down after 15 min of inactivity (cold start ~30s).
> Upgrade to Starter ($7/mo) for always-on.

---

## 2. Build Mobile App (Expo)

### Prerequisites
```bash
npm install -g expo-cli eas-cli
```

### Step 1 — Set your backend URL
Edit `mobile/src/lib/config.ts`:
```typescript
export const API_BASE_URL = "https://trading-signal-agent-api.onrender.com";
```
Or create `mobile/.env`:
```
EXPO_PUBLIC_API_URL=https://trading-signal-agent-api.onrender.com
```

### Step 2 — Run locally on your phone
```bash
cd mobile
npm install
npx expo start
```
Scan the QR code with **Expo Go** app (iOS/Android) — instant preview!

### Step 3 — Build APK for Android (free)
```bash
cd mobile
eas login          # create free Expo account
eas build:configure
eas build --platform android --profile preview
```
This builds an `.apk` you can install directly on any Android device.

### Step 4 — Build for iOS (requires Apple Developer account $99/yr)
```bash
eas build --platform ios
```

### Step 5 — Submit to stores
```bash
eas submit --platform android   # Google Play Store
eas submit --platform ios       # Apple App Store
```

---

## 3. Development — run everything locally

### Backend
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Mobile (connects to localhost)
```bash
cd mobile
EXPO_PUBLIC_API_URL=http://YOUR_LOCAL_IP:8000 npx expo start
```
> Use your machine's local IP (not localhost) so the phone can reach it on WiFi.

---

## Architecture Summary

```
[Expo Mobile App] ──── HTTPS ───→ [Render Backend (FastAPI)]
                                          │
                              ┌───────────┼──────────────┐
                         yfinance    CoinGecko       NewsAPI/RSS
                              └───────────┼──────────────┘
                                     Claude API
                                   (Signal Brain)
                                          │
                                     SQLite DB
                                          │
                                  Telegram Alerts
```
