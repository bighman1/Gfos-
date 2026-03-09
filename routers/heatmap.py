from fastapi import APIRouter
from datetime import datetime, timezone
import store
from routers.corridors import CORRIDOR_RAIL_MAP, compute_shares, get_rail_data

router = APIRouter()

@router.get("/snapshot")
async def get_heatmap_snapshot():
    now = datetime.now(timezone.utc).isoformat()
    corridor_scores = {}
    for code, config in CORRIDOR_RAIL_MAP.items():
        shares = compute_shares(config)
        avg_vol = sum(
            get_rail_data(s["rail"]).get("volume_index", 40)
            for s in shares
        ) / max(len(shares), 1)
        corridor_scores[code] = round(avg_vol, 1)

    sorted_c = sorted(corridor_scores.items(), key=lambda x: x[1], reverse=True)
    hotspots  = [{"corridor": c, "intensity": round(v/100, 2)} for c, v in sorted_c[:4]]
    cold_zones= [{"corridor": c, "intensity": round(v/100, 2)} for c, v in sorted_c[-3:]]

    shifts = []
    for code, config in CORRIDOR_RAIL_MAP.items():
        shares = compute_shares(config)
        avg_trend = sum(s.get("trend", 0) for s in shares) / max(len(shares), 1)
        if abs(avg_trend) >= 15:
            shifts.append({"corridor": code, "change_pct": round(avg_trend,1), "direction": "inflow" if avg_trend>0 else "outflow"})
    shifts.sort(key=lambda s: abs(s["change_pct"]), reverse=True)

    banking    = store.get_sync("rails:banking",    {})
    remittance = store.get_sync("rails:remittance", {})
    mobile     = store.get_sync("rails:mobile",     {})
    crypto     = store.get_sync("rails:crypto",     {})

    by_category = {}
    for cat_name, cat_rails in [("banking",banking),("remittance",remittance),("mobile_money",mobile),("crypto",crypto)]:
        top = sorted(cat_rails.values(), key=lambda r: r.get("volume_index",0), reverse=True)[:3]
        by_category[cat_name] = [{"corridor": r.get("active_corridors",["global"])[0], "intensity": round(r.get("volume_index",50)/100,2)} for r in top]

    return {"hotspots": hotspots, "cold_zones": cold_zones, "shifts": shifts, "by_category": by_category, "generated_at": now}
