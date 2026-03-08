"""
GFOS API Router — FX Markets
Live exchange rates and cross-rail FX pressure signals.
"""

from fastapi import APIRouter, HTTPException
from models import FXSignal, FXRates
import store

router = APIRouter()


@router.get("/rates", response_model=FXRates)
async def get_fx_rates():
    """Live FX rates for all pairs (170+ currencies, USD base)."""
    rates = store.get_sync("fx:rates")
    if not rates:
        raise HTTPException(status_code=503, detail="FX rates not yet loaded — try again in 30 seconds")
    return rates


@router.get("/{pair}/signal", response_model=FXSignal)
async def get_fx_signal(pair: str):
    """
    FX intelligence for a currency pair.
    Includes cross-rail pressure signal — where is FX stress appearing?
    """
    signals = store.get_sync("fx:signals", {})
    pair_upper = pair.upper().replace("-", "/")

    signal = signals.get(pair_upper)
    if not signal:
        raise HTTPException(
            status_code=404,
            detail=f"Pair '{pair}' not tracked. Available: {list(signals.keys())}"
        )
    return signal


@router.get("/signals")
async def list_fx_signals():
    """All tracked corridor FX signals."""
    signals = store.get_sync("fx:signals", {})
    return {"signals": list(signals.values())}
