from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timezone
import store

router = APIRouter()

CORRIDOR_RAIL_MAP = {
    "KE-DE": {
        "source": "Kenya", "destination": "Germany",
        "rails": [
            {"rail": "M-Pesa",       "category": "mobile_money", "base_share": 40},
            {"rail": "USDC/Solana",  "category": "crypto",       "base_share": 22},
            {"rail": "Wise",         "category": "remittance",   "base_share": 20},
            {"rail": "SWIFT",        "category": "banking",      "base_share": 12},
            {"rail": "Western Union","category": "remittance",   "base_share": 6},
        ],
    },
    "US-MX": {
        "source": "USA", "destination": "Mexico",
        "rails": [
            {"rail": "Remitly",      "category": "remittance",   "base_share": 35},
            {"rail": "ACH",          "category": "banking",      "base_share": 25},
            {"rail": "Wise",         "category": "remittance",   "base_share": 20},
            {"rail": "USDT/TRON",    "category": "crypto",       "base_share": 12},
            {"rail": "Western Union","category": "remittance",   "base_share": 8},
        ],
    },
    "UK-NG": {
        "source": "UK", "destination": "Nigeria",
        "rails": [
            {"rail": "WorldRemit",   "category": "remittance",   "base_share": 38},
            {"rail": "MTN MoMo",     "category": "mobile_money", "base_share": 28},
            {"rail": "Sendwave",     "category": "remittance",   "base_share": 18},
            {"rail": "USDT/TRON",    "category": "crypto",       "base_share": 10},
            {"rail": "SWIFT",        "category": "banking",      "base_share": 6},
        ],
    },
    "CN-AF": {
        "source": "China", "destination": "Africa",
        "rails": [
            {"rail": "CIPS",         "category": "banking",      "base_share": 55},
            {"rail": "MTN MoMo",     "category": "mobile_money", "base_share": 22},
            {"rail": "USDT/TRON",    "category": "crypto",       "base_share": 15},
            {"rail": "SWIFT",        "category": "banking",      "base_share": 8},
        ],
    },
    "SN-FR": {
        "source": "Senegal", "destination": "France",
        "rails": [
            {"rail": "Wave",         "category": "mobile_money", "base_share": 55},
            {"rail": "Orange Money", "category": "mobile_money", "base_share": 22},
            {"rail": "SEPA Instant", "category": "banking",      "base_share": 14},
            {"rail": "SWIFT",        "category": "banking",      "base_share": 9},
        ],
    },
    "US-IN": {
        "source": "USA", "destination": "India",
        "rails": [
            {"rail": "Wise",         "category": "remittance",   "base_share": 40},
            {"rail": "Remitly",      "category": "remittance",   "base_share": 28},
            {"rail": "SWIFT",        "category": "banking",      "base_share": 18},
            {"rail": "USDC/Solana",  "category": "crypto",       "base_share": 9},
            {"rail": "Western Union","category": "remittance",   "base_share": 5},
        ],
    },
}

SPEED_MAP = {
    "M-Pesa": "~10 seconds", "MTN MoMo": "~15 seconds",
    "Wave": "~5 seconds", "USDT/TRON": "~3 seconds",
    "USDC/Solana": "~5 seconds", "Stellar XLM": "~5 seconds",
    "Wise": "~2 hours", "WorldRemit": "~1 hour",
    "Remitly": "~1 hour", "Sendwave": "~30 minutes",
    "Western Union": "~30 minutes", "SEPA Instant": "~10 seconds",
    "ACH": "1-3 days", "SWIFT": "2-5 days",
    "CIPS": "~4 hours", "Orange Money": "~15 seconds",
}

def get_rail_data(rail_name):
    for key in ["rails:banking","rails:remittance","rails:mobile","rails:crypto"]:
        cat = store.get_sync(key, {})
        if rail_name in cat:
            return cat[rail_name]
    return {}

def compute_shares(config):
    rails = config["rails"]
    weighted = []
    for r in rails:
        data = get_rail_data(r["rail"])
        signal = data.get("volume_signal", "stable")
        multiplier = {"surging":1.4,"rising":1.2,"stable":1.0,"declining":0.8,"draining":0.6}.get(signal, 1.0)
        weighted.append({**r, "weighted": r["base_share"] * multiplier,
                         "volume_signal": signal,
                         "trend": data.get("volume_change_pct", 0)})
    total = sum(r["weighted"] for r in weighted) or 1
    for r in weighted:
        r["share_pct"] = round((r["weighted"] / total) * 100, 1)
    return sorted(weighted, key=lambda r: r["share_pct"], reverse=True)

@router.get("")
async def list_corridors():
    return {"corridors": [
        {"code": code, "source": c["source"], "destination": c["destination"], "rail_count": len(c["rails"])}
        for code, c in CORRIDOR_RAIL_MAP.items()
    ]}

@router.get("/{corridor}/intelligence")
async def get_corridor_intelligence(corridor: str):
    config = CORRIDOR_RAIL_MAP.get(corridor.upper())
    if not config:
        raise HTTPException(status_code=404, detail=f"Corridor '{corridor}' not found")
    now = datetime.now(timezone.utc).isoformat()
    shares = compute_shares(config)
    avg_trend = sum(s["trend"] * s["share_pct"] / 100 for s in shares)
    avg_cong = sum(
        get_rail_data(s["rail"]).get("congestion_score", 20) * s["share_pct"] / 100
        for s in shares
    )
    return {
        "source_country":      config["source"],
        "destination_country": config["destination"],
        "dominant_rail":       shares[0]["rail"] if shares else "Unknown",
        "volume_trend":        f"{'+' if avg_trend >= 0 else ''}{avg_trend:.1f}% WoW",
        "volume_signal":       "surging" if avg_trend>=30 else "rising" if avg_trend>=10 else "stable" if avg_trend>=-10 else "declining",
        "volume_change_pct":   round(avg_trend, 1),
        "congestion_level":    "high" if avg_cong>=60 else "medium" if avg_cong>=30 else "low",
        "liquidity_signal":    "deep" if avg_trend>=10 else "moderate" if avg_trend>=-10 else "shallow",
        "rail_breakdown":      [{"rail":s["rail"],"category":s["category"],"share_pct":s["share_pct"],"volume_signal":s["volume_signal"],"trend":"rising" if s["trend"]>5 else "stable" if s["trend"]>=-5 else "declining"} for s in shares],
        "observed_at":         now,
    }

@router.get("/{corridor}/rails/compare")
async def compare_corridor_rails(corridor: str, rails: Optional[str] = Query(None)):
    config = CORRIDOR_RAIL_MAP.get(corridor.upper())
    if not config:
        raise HTTPException(status_code=404, detail=f"Corridor '{corridor}' not found")
    now = datetime.now(timezone.utc).isoformat()
    rail_filter = set(rails.split(",")) if rails else None
    rows = []
    for r in config["rails"]:
        if rail_filter and r["rail"] not in rail_filter:
            continue
        data = get_rail_data(r["rail"])
        trend = data.get("volume_change_pct", 0)
        rows.append({
            "name":             r["rail"],
            "category":         r["category"],
            "volume_index":     data.get("volume_index", 50),
            "fee_index":        data.get("fee_index", 50),
            "speed_index":      data.get("speed_index", 50),
            "congestion_level": data.get("congestion_level", "low"),
            "avg_speed":        SPEED_MAP.get(r["rail"], "Unknown"),
            "volume_signal":    data.get("volume_signal", "stable"),
            "signal":           data.get("signal", ""),
            "trend":            "rising" if trend>5 else "stable" if trend>=-5 else "declining",
        })
    rows.sort(key=lambda r: r["volume_index"], reverse=True)
    return {"source_country": config["source"], "destination_country": config["destination"], "rails": rows, "compared_at": now}
