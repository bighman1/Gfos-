from fastapi import APIRouter, HTTPException
import store

router = APIRouter()

@router.get("/rates")
async def get_fx_rates():
    rates = store.get_sync("fx:rates")
    if not rates:
        raise HTTPException(status_code=503, detail="FX rates not yet loaded — try again in 30 seconds")
    return rates

@router.get("/signals")
async def list_fx_signals():
    signals = store.get_sync("fx:signals", {})
    return {"signals": list(signals.values())}

@router.get("/{pair}/signal")
async def get_fx_signal(pair: str):
    signals = store.get_sync("fx:signals", {})
    pair_upper = pair.upper().replace("-", "/")
    signal = signals.get(pair_upper)
    if not signal:
        raise HTTPException(status_code=404, detail=f"Pair '{pair}' not tracked. Available: {list(signals.keys())}")
    return signal
