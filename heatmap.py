"""
GFOS API Router — Heatmap
Global liquidity heatmap endpoints.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
from models import HeatmapSnapshot, HeatmapEntry, HeatmapShift
import store

router = APIRouter()


@router.get("/snapshot", response_model=HeatmapSnapshot)
async def get_heatmap_snapshot():
    """Global liquidity heatmap — all rail categories."""
    now = datetime.now(timezone.utc).isoformat()

    # Pull all rail data
    banking    = store.get_sync("rails:banking",    {})
    remittance = store.get_sync("rails:remittance", {})
    mobile     = store.get_sync("rails:mobile",     {})
    crypto     = store.get_sync("rails:crypto",     {})
    all_rails  = {**banking, **remittance, **mobile, **crypto}

    # Build corridor intensities from rail data
    corridor_scores = {}
    from routers.corridors import CORRIDOR_RAIL_MAP, compute_corridor_shares

    for code, config in CORRIDOR_RAIL_MAP.items():
        shares = compute_corridor_shares(config)
        avg_volume = sum(
            store.get_sync("rails:banking",    {}).get(s["rail"], {}).get("volume_index", 0) or
            store.get_sync("rails:remittance", {}).get(s["rail"], {}).get("volume_index", 0) or
            store.get_sync("rails:mobile",     {}).get(s["rail"], {}).get("volume_index", 0) or
            store.get_sync("rails:crypto",     {}).get(s["rail"], {}).get("volume_index", 0) or 40
            for s in shares
        ) / max(len(shares), 1)
        corridor_scores[code] = round(avg_volume, 1)

    sorted_corridors = sorted(corridor_scores.items(), key=lambda x: x[1], reverse=True)

    hotspots  = [HeatmapEntry(corridor=c, intensity=v/100) for c, v in sorted_corridors[:4]]
    cold_zones= [HeatmapEntry(corridor=c, intensity=v/100) for c, v in sorted_corridors[-3:]]

    # Shifts — corridors with strongest trend movement
    shifts = []
    for code, config in CORRIDOR_RAIL_MAP.items():
        shares = compute_corridor_shares(config)
        avg_trend = sum(s.get("trend", 0) for s in shares) / max(len(shares), 1)
        if abs(avg_trend) >= 15:
            shifts.append(HeatmapShift(
                corridor=code,
                change_pct=round(avg_trend, 1),
                direction="inflow" if avg_trend > 0 else "outflow",
            ))
    shifts.sort(key=lambda s: abs(s.change_pct), reverse=True)

    # By category breakdown
    by_category = {}
    for cat_name, cat_rails in [("banking", banking), ("remittance", remittance), ("mobile_money", mobile), ("crypto", crypto)]:
        top_rails = sorted(cat_rails.values(), key=lambda r: r.get("volume_index", 0), reverse=True)[:3]
        by_category[cat_name] = [
            {"corridor": r["active_corridors"][0] if r.get("active_corridors") else "global",
             "intensity": round(r.get("volume_index", 50) / 100, 2)}
            for r in top_rails
        ]

    return HeatmapSnapshot(
        hotspots=hotspots,
        cold_zones=cold_zones,
        shifts=shifts,
        by_category=by_category,
        generated_at=now,
    )
