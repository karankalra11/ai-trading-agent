from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .api.routes_signals import router as signals_router
from .api.routes_market import router as market_router
from .api.routes_news import router as news_router
from .scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting AI Trading Signal Agent …")
    init_db()

    # Pre-load sentiment model in background to avoid cold start on first request
    try:
        from .sentiment.model_loader import get_sentiment_pipeline
        get_sentiment_pipeline()
    except Exception as e:
        print(f"⚠️  Sentiment model pre-load failed: {e} (will load on first use)")

    start_scheduler()
    yield

    # Shutdown
    stop_scheduler()
    print("👋 Shutting down")


app = FastAPI(
    title="AI Trading Signal Agent",
    description="Real-time BUY/SELL/HOLD signals for US, India, Crypto & ETF markets",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(signals_router)
app.include_router(market_router)
app.include_router(news_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "trading-signal-agent"}
