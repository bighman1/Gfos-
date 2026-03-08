"""
GFOS Backend — Global Financial Operating System
FastAPI intelligence server

Live data sources:
  - CoinGecko API   (crypto fees, volumes)     — free, no key needed
  - Open Exchange Rates                         — free tier, key required
  - Synthetic monitors                          — realistic rail signals

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload

Deploy to Railway / Render / Fly.io — see README.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from routers import rails, corridors, heatmap, fx, analysis
from collectors.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background data collectors on boot, stop on shutdown."""
    await start_scheduler()
    yield
    await stop_scheduler()


app = FastAPI(
    title="GFOS Intelligence API",
    description="Global Financial Operating System — Rail Intelligence Layer",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS — allow the React dashboard to call this API ────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this to your Vercel URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────
app.include_router(rails.router,     prefix="/v1/rails",      tags=["Rails"])
app.include_router(corridors.router, prefix="/v1/corridors",  tags=["Corridors"])
app.include_router(heatmap.router,   prefix="/v1/heatmap",    tags=["Heatmap"])
app.include_router(fx.router,        prefix="/v1/fx",         tags=["FX"])
app.include_router(analysis.router,  prefix="/v1/intelligence",tags=["Intelligence"])


@app.get("/")
async def root():
    return {
        "name": "GFOS Intelligence API",
        "version": "0.1.0",
        "status": "live",
        "docs": "/docs",
        "note": "GFOS observes payment rails. It does not process payments."
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
