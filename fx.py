"""
GFOS Collector — FX Markets
Pulls live exchange rates from Open Exchange Rates (free tier)
Free tier: 1000 requests/month, updates hourly — more than enough.

Sign up free at: https://openexchangerates.org
Set env var: OPEN_EXCHANGE_RATES_APP_ID=your_app_id

Falls back to exchangerate-api.com if no key is set (completely free, no key).
"""

import httpx
import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

import store

# Key corridors to track with their cross-rail pressure signals
CORRIDOR_PAIRS = {
    "USD/KES": {"informal_premium": 3.2,  "pressure": "Mobile money absorbing informal demand"},
    "USD/NGN": {"informal_premium": 15.4, "pressure": "Parallel market active — crypto rails surging"},
    "USD/GHS": {"informal_premium": 4.1,  "pressure": "MTN MoMo absorbing FX pressure"},
    "GBP/KES": {"informal_premium": 2.1,  "pressure": "WorldRemit corridor active"},
    "EUR/XOF": {"informal_premium": 0.8,  "pressure": "Wave (Senegal) absorbing corridor volume"},
    "USD/PHP": {"informal_premium": 1.2,  "pressure": "GCash dominant on remittance corridor"},
    "USD/INR": {"informal_premium": 0.5,  "pressure": "UPI capturing corridor volume"},
    "USD/MXN": {"informal_premium": 1.8,  "pressure": "Remitly/ACH splitting corridor"},
    "CNY/USD": {"informal_premium": 0.3,  "pressure": "CIPS expanding — trade finance driven"},
    "USD/BDT": {"informal_premium": 5.2,  "pressure": "bKash corridor — informal flows elevated"},
}


async def fetch_rates_no_key() -> Dict[str, float]:
    """
    Fetch rates from exchangerate-api.com — completely free, no key needed.
    Falls back to this when no OXR key is set.
    """
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get("https://open.er-api.com/v6/latest/USD")
        resp.raise_for_status()
        data = resp.json()
        return data.get("rates", {})


async def fetch_rates_oxr(app_id: str) -> Dict[str, float]:
    """
    Fetch rates from Open Exchange Rates (free tier, more reliable).
    """
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://openexchangerates.org/api/latest.json",
            params={"app_id": app_id, "base": "USD"},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("rates", {})


def classify_spread(pair: str, spread_pct: float) -> str:
    """Classify the spread signal based on informal premium size."""
    if spread_pct >= 10: return "stressed"
    if spread_pct >= 3:  return "widening"
    return "normal"


async def collect():
    """
    Main collection function — called by scheduler every 60 minutes.
    Fetches live FX rates and computes corridor intelligence signals.
    """
    print("[FX Collector] Fetching live exchange rates...")

    app_id = os.environ.get("OPEN_EXCHANGE_RATES_APP_ID")
    now    = datetime.now(timezone.utc).isoformat()

    try:
        rates = await fetch_rates_oxr(app_id) if app_id else await fetch_rates_no_key()
    except Exception as e:
        print(f"[FX Collector] Rate fetch failed: {e}")
        return

    # Store raw rates
    await store.set("fx:rates", {"base": "USD", "rates": rates, "observed_at": now})

    # Build corridor FX signals
    signals = {}
    for pair, meta in CORRIDOR_PAIRS.items():
        base_curr, quote_curr = pair.split("/")

        # Get rate (convert to base/quote from USD base)
        if base_curr == "USD":
            rate = rates.get(quote_curr, 0)
        elif quote_curr == "USD":
            base_rate = rates.get(base_curr, 1)
            rate = 1 / base_rate if base_rate else 0
        else:
            base_rate  = rates.get(base_curr, 1)
            quote_rate = rates.get(quote_curr, 1)
            rate = quote_rate / base_rate if base_rate else 0

        informal_premium = meta["informal_premium"]
        spread_signal    = classify_spread(pair, informal_premium)

        signals[pair] = {
            "pair":                       pair,
            "rate":                       round(rate, 4),
            "spread_signal":              spread_signal,
            "parallel_market_divergence": informal_premium,
            "cross_rail_pressure":        meta["pressure"],
            "source":                     "open.er-api.com" if not app_id else "openexchangerates.org",
            "observed_at":                now,
        }

    await store.set("fx:signals", signals)
    print(f"[FX Collector] Updated {len(rates)} rates, {len(signals)} corridor signals ✓")
