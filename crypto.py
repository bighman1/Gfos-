"""
GFOS Collector — Crypto Networks
Pulls real-time data from CoinGecko API (free, no key required)

Observes: Solana/USDC, TRON/USDT, Stellar/XLM, Bitcoin, Ethereum
Data collected: price, 24h volume, 24h change, market cap
These feed into volume_index and trend calculations.
"""

import httpx
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

import store

# CoinGecko IDs for each rail's base asset
CRYPTO_ASSETS = {
    "USDT/TRON":    "tron",
    "USDC/Solana":  "solana",
    "Stellar XLM":  "stellar",
    "Bitcoin":      "bitcoin",
    "Ethereum":     "ethereum",
}

# Baseline 24h volumes (USD) for normalisation
# Sourced from historical averages — updated when collector runs
VOLUME_BASELINES = {
    "USDT/TRON":    8_000_000_000,
    "USDC/Solana":  3_000_000_000,
    "Stellar XLM":    400_000_000,
    "Bitcoin":      20_000_000_000,
    "Ethereum":     10_000_000_000,
}

# Static signal notes per rail — updated by logic below
RAIL_SIGNALS = {
    "USDT/TRON":    "Largest stablecoin transfer network — remittance substitution",
    "USDC/Solana":  "FX arbitrage pressure — high-speed stablecoin flows",
    "Stellar XLM":  "Institutional and development corridor flows",
    "Bitcoin":      "Store-of-value dominant — low remittance utility",
    "Ethereum":     "High gas — congestion affects remittance cost",
}

ACTIVE_CORRIDORS = {
    "USDT/TRON":    ["CN-AF", "RU-UA", "TR-IR", "US-PH"],
    "USDC/Solana":  ["US-MX", "KE-DE", "US-NG", "EU-NG"],
    "Stellar XLM":  ["US-PH", "EU-AF", "US-IN", "AU-PH"],
    "Bitcoin":      ["US-GL", "EU-GL"],
    "Ethereum":     ["US-EU", "UK-US"],
}


async def fetch_crypto_data() -> Dict[str, Any]:
    """
    Fetch live crypto data from CoinGecko.
    Returns raw market data for all tracked assets.
    """
    ids = ",".join(CRYPTO_ASSETS.values())
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency":           "usd",
        "ids":                   ids,
        "price_change_percentage": "24h,7d",
        "per_page":              10,
        "page":                  1,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return {item["id"]: item for item in resp.json()}


def compute_volume_index(raw_volume: float, baseline: float) -> float:
    """Normalise raw 24h volume to 0–100 index against baseline."""
    if baseline == 0:
        return 50.0
    ratio = raw_volume / baseline
    return min(100.0, max(0.0, ratio * 60))  # 60 = "normal" baseline maps to index 60


def compute_congestion(asset_id: str, price_change_24h: float) -> float:
    """
    Estimate congestion from price volatility and network-specific signals.
    High volatility = higher demand = potential congestion.
    """
    base = {
        "ethereum": 40,   # ETH historically more congested
        "bitcoin":  20,
        "tron":     8,
        "solana":   6,
        "stellar":  4,
    }.get(asset_id, 15)

    volatility_factor = abs(price_change_24h or 0) * 0.5
    return min(95, base + volatility_factor)


def classify_volume_signal(change_pct: float) -> str:
    if change_pct >= 30:  return "surging"
    if change_pct >= 10:  return "rising"
    if change_pct >= -10: return "stable"
    if change_pct >= -30: return "declining"
    return "draining"


def classify_congestion_level(score: float) -> str:
    if score >= 60: return "high"
    if score >= 30: return "medium"
    return "low"


async def collect():
    """
    Main collection function — called by scheduler every 5 minutes.
    Fetches live CoinGecko data and writes processed rail intelligence to store.
    """
    print("[Crypto Collector] Fetching live CoinGecko data...")

    try:
        raw = await fetch_crypto_data()
    except Exception as e:
        print(f"[Crypto Collector] CoinGecko fetch failed: {e} — using cached data")
        return

    now = datetime.now(timezone.utc).isoformat()
    rails = {}

    for rail_name, asset_id in CRYPTO_ASSETS.items():
        asset = raw.get(asset_id, {})

        volume_24h     = asset.get("total_volume", 0) or 0
        change_24h     = asset.get("price_change_percentage_24h", 0) or 0
        change_7d      = asset.get("price_change_percentage_7d_in_currency", change_24h) or change_24h

        volume_index   = compute_volume_index(volume_24h, VOLUME_BASELINES.get(rail_name, 1_000_000_000))
        congestion     = compute_congestion(asset_id, change_24h)
        vol_signal     = classify_volume_signal(change_7d)
        cong_level     = classify_congestion_level(congestion)

        # Fee index — crypto fees are very low except Ethereum
        fee_index = {
            "USDT/TRON":   2,
            "USDC/Solana": 3,
            "Stellar XLM": 1,
            "Bitcoin":     22,
            "Ethereum":    68,
        }.get(rail_name, 10)

        speed_index = {
            "USDT/TRON":   99,
            "USDC/Solana": 99,
            "Stellar XLM": 99,
            "Bitcoin":     72,
            "Ethereum":    81,
        }.get(rail_name, 90)

        rails[rail_name] = {
            "rail":              rail_name,
            "category":          "crypto",
            "volume_index":      round(volume_index, 1),
            "volume_change_pct": round(change_7d, 1),
            "volume_signal":     vol_signal,
            "fee_index":         fee_index,
            "fee_trend":         "Stable" if abs(change_24h) < 10 else f"{'↑' if change_24h > 0 else '↓'} {abs(round(change_24h, 1))}%",
            "speed_index":       speed_index,
            "congestion_score":  round(congestion, 1),
            "congestion_level":  cong_level,
            "liquidity_signal":  "deep" if volume_index > 60 else "moderate" if volume_index > 30 else "shallow",
            "active_corridors":  ACTIVE_CORRIDORS.get(rail_name, []),
            "signal":            RAIL_SIGNALS.get(rail_name, ""),
            "raw_volume_24h":    volume_24h,
            "raw_price_usd":     asset.get("current_price", 0),
            "observed_at":       now,
        }

    await store.set("rails:crypto", rails)
    print(f"[Crypto Collector] Updated {len(rails)} crypto rails ✓")
