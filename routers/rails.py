from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timezone
import store

router = APIRouter()

def get_all_rails():
    banking    = store.get_sync("rails:banking",    {})
    remittance = store.get_sync("rails:remittance", {})
    mobile     = store.get_sync("rails:mobile",     {})
    crypto     = store.get_sync("rails:crypto",     {})
    return {**banking, **remittance, **mobile, **crypto}

@router.get("")
async def get_all_rails_endpoint():
    all_rails = get_all_rails()
    rails = list(all_rails.values())
    rails.sort(key=lambda r: r["volume_index"], reverse=True)
    return rails

@router.get("/surging")
async def get_surging_rails(
    threshold: float = Query(0.15),
    categories: Optional[str] = Query(None),
):
    all_rails = get_all_rails()
    threshold_pct = threshold * 100 if threshold <= 1 else threshold
    cat_filter = set(categories.split(",")) if categories else None
    surging = [
        rail for rail in all_rails.values()
        if rail["volume_change_pct"] >= threshold_pct
        and (not cat_filter or rail["category"] in cat_filter)
    ]
    surging.sort(key=lambda r: r["volume_change_pct"], reverse=True)
    return surging

@router.get("/congested")
async def get_congested_rails():
    all_rails = get_all_rails()
    congested = [
        rail for rail in all_rails.values()
        if rail["congestion_level"] in ("medium", "high")
    ]
    congested.sort(key=lambda r: r["congestion_score"], reverse=True)
    return congested

@router.get("/category/{category}")
async def get_rails_by_category(category: str):
    category_map = {
        "banking":      store.get_sync("rails:banking",    {}),
        "remittance":   store.get_sync("rails:remittance", {}),
        "mobile_money": store.get_sync("rails:mobile",     {}),
        "crypto":       store.get_sync("rails:crypto",     {}),
    }
    if category not in category_map:
        raise HTTPException(status_code=400, detail=f"Unknown category '{category}'")
    rails = list(category_map[category].values())
    rails.sort(key=lambda r: r["volume_index"], reverse=True)
    return rails

@router.get("/{rail}/intelligence")
async def get_rail_intelligence(rail: str):
    all_rails = get_all_rails()
    match = next(
        (v for k, v in all_rails.items() if k.lower() == rail.lower()),
        None
    )
    if not match:
        raise HTTPException(status_code=404, detail=f"Rail '{rail}' not found")
    return match

@router.get("/{rail}/history")
async def get_rail_history(rail: str, days: int = 30):
    return {
        "rail": rail,
        "days": days,
        "message": "Historical data coming in Phase 2",
        "observed_at": datetime.now(timezone.utc).isoformat()
  }
