"""
GFOS API Router — Corridors
Corridor intelligence and cross-rail comparison endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timezone

import store
from models import CorridorIntelligence, RailComparison, RailShare, RailComparisonRow

router = APIRouter()

# ── Corridor definitions ──────────────────────────────────────────
# Which rails are active on which corridors, and their typical share weights.
# In Phase 2 these weights come from live data.

CORRIDOR_RAIL_MAP = {
    "KE-DE": {
        "source": "Kenya", "destination": "Germany",
        "rails": [
            {"rail": "M-Pesa",      "category": "mobile_money", "base_share": 40},
            {"rail": "USDC/Solana", "category": "crypto",       "base_share": 22},
            {"rail": "Wise",        "category": "remittance",   "base_share": 20},
            {"rail": "SWIFT",       "category": "banking",      "base_share": 12},
            {"rail": "Western Union","category": "remittance",  "base_share": 6},
        ],
    },
    "US-MX": {
        "source": "USA", "destination": "Mexico",
        "rails": [
            {"rail": "Remitly",     "category": "remittance",   "base_share": 35},
            {"rail": "ACH",         "category": "banking",      "base_share": 25},
            {"rail": "Wise",        "category": "remittance",   "base_share": 20},
            {"rail": "USDT/TRON",   "category": "crypto",       "base_share": 12},
            {"rail": "Western Union","category": "remittance",  "base_share": 8},
        ],
    },
    "UK-NG": {
        "source": "UK", "destination": "Nigeria",
        "rails": [
            {"rail": "WorldRemit",  "category": "remittance",   "base_share": 38},
            {"rail": "MTN MoMo",    "category": "mobile_money", "base_share": 28},
            {"rail": "Sendwave",    "category": "remittance",   "base_share": 18},
            {"rail": "USDT/TRON",   "category": "crypto",       "base_share": 10},
            {"rail": "SWIFT",       "category": "banking",      "base_share": 6},
        ],
    },
    "CN-AF": {
        "source": "China", "destination": "Africa",
        "rails": [
            {"rail": "CIPS",        "category": "banking",      "base_share": 55},
            {"rail": "MTN MoMo",    "category": "mobile_money", "base_share": 22},
            {"rail": "USDT/TRON",   "category": "crypto",       "base_share": 15},
            {"rail": "SWIFT",       "category": "banking",      "base_share": 8},
        ],
    },
    "US-IN": {
        "source": "USA", "destination": "India",
        "rails": [
            {"rail": "Wise",        "category": "remittance",   "base_share": 40},
            {"rail": "Remitly",     "category": "remittance",   "base_share": 28},
            {"rail": "SWIFT",       "category": "banking",      "base_share": 18},
            {"rail": "USDC/Solana", "category": "crypto",       "base_share": 9},
            {"rail": "Western Union","category": "remittance",  "base_share": 5},
        ],
    },
    "EU-PH": {
        "source": "Europe", "destination": "Philippines",
        "rails": [
            {"rail": "Sendwave",    "category": "remittance",   "base_share": 35},
            {"rail": "Wise",        "category": "remittance",   "base_share": 28},
            {"rail": "SEPA Instant","category": "banking",      "base_share": 20},
            {"rail": "USDT/TRON",   "category": "crypto",       "base_share": 12},
            {"rail": "SWIFT",       "category": "banking",      "base_share": 5},
        ],
    },
    "GH-UK": {
        "source": "Ghana", "destination": "UK",
        "rails": [
            {"rail": "MTN MoMo",    "category": "mobile_money", "base_share": 42},
            {"rail": "Sendwave",    "category": "remittance",   "base_share": 28},
            {"rail": "WorldRemit",  "category": "remittance",   "base_share": 18},
            {"rail": "SWIFT",       "category": "banking",      "base_share": 12},
        ],
    },
    "SN-FR": {
        "source": "Senegal", "destination": "France",
        "rails": [
            {"rail": "Wave",        "category": "mobile_money", "base_share": 55},
            {"rail": "Orange Money","category": "mobile_money", "base_share": 22},
            {"rail": "SEPA Instant","category": "banking",      "base_share": 14},
            {"rail": "SWIFT",       "category": "banking",      "base_share": 9},
        ],
    },
}

SPEED_MAP = {
    "M-Pesa":       "~10 seconds",
    "MTN MoMo":     "~15 seconds",
    "Wave":         "~5 seconds",
    "Airtel Money": "~12 seconds",
    "Orange Money": "~15 seconds",
    "USDT/TRON":    "~3 seconds",
    "USDC/Solana":  "~5 seconds",
    "Stellar XLM":  "~5 seconds",
    "Bitcoin":      "~10 minutes",
    "Ethereum":     "~2 minutes",
    "Wise":         "~2 hours",
    "WorldRemit":   "~1 hour",
    "Remitly":      "~1 hour",
    "Sendwave":     "~30 minutes",
    "Western Union":"~30 minutes",
    "SEPA Instant": "~10 seconds",
    "ACH":          "1-3 days",
    "SWIFT":        "2-5 days",
    "Fedwire":      "Same day",
    "CHAPS":        "Same day",
    "CIPS":         "~4 hours",
}


def get_rail_data(rail_name: str) -> dict:
    """Fetch current rail data from store."""
    all_cats = ["rails:banking", "rails:remittance", "rails:mobile", "rails:crypto"]
    for cat_key in all_cats:
        cat = store.get_sync(cat_key, {})
        if rail_name in cat:
            return cat[rail_name]
    return {}


def compute_corridor_shares(corridor_config: dict) -> List[dict]:
    """
    Compute real-time corridor shares by weighting base shares
    against current rail volume signals.
    """
    rails = corridor_config["rails"]
    weighted = []

    for rail_def in rails:
        rail_data = get_rail_data(rail_def["rail"])
        volume_signal = rail_data.get("volume_signal", "stable")
        trend = rail_data.get("volume_change_pct", 0)

        # Weight the base share by live volume signal
        multiplier = {
            "surging":  1.4,
            "rising":   1.2,
            "stable":   1.0,
            "declining":0.8,
            "draining": 0.6,
        }.get(volume_signal, 1.0)

        weighted.append({
            "rail":          rail_def["rail"],
            "category":      rail_def["category"],
            "weighted_share":rail_def["base_share"] * multiplier,
            "volume_signal": volume_signal,
            "trend":         trend,
        })

    # Normalise to 100%
    total = sum(r["weighted_share"] for r in weighted)
    for r in weighted:
        r["share_pct"] = round((r["weighted_share"] / total) * 100, 1) if total else 0

    weighted.sort(key=lambda r: r["share_pct"], reverse=True)
    return weighted


@router.get("/{corridor}/intelligence", response_model=CorridorIntelligence)
async def get_corridor_intelligence(corridor: str, period: str = "7d"):
    """
    Full intelligence snapshot for a corridor — across ALL rail categories.
    """
    corridor_upper = corridor.upper()
    config = CORRIDOR_RAIL_MAP.get(corridor_upper)

    if not config:
        raise HTTPException(status_code=404, detail=f"Corridor '{corridor}' not found. Available: {list(CORRIDOR_RAIL_MAP.keys())}")

    now    = datetime.now(timezone.utc).isoformat()
    shares = compute_corridor_shares(config)

    dominant_rail = shares[0]["rail"] if shares else "Unknown"
    top_trend     = shares[0]["trend"] if shares else 0

    # Overall corridor metrics
    avg_trend  = sum(s["trend"] * s["share_pct"] / 100 for s in shares)
    avg_signal = "surging" if avg_trend >= 30 else "rising" if avg_trend >= 10 else "stable" if avg_trend >= -10 else "declining"
    avg_cong   = sum(
        (get_rail_data(s["rail"]).get("congestion_score", 20)) * s["share_pct"] / 100
        for s in shares
    )
    cong_level = "high" if avg_cong >= 60 else "medium" if avg_cong >= 30 else "low"
    liq_signal = "deep" if avg_trend >= 10 else "moderate" if avg_trend >= -10 else "shallow"

    rail_breakdown = [
        RailShare(
            rail=s["rail"],
            category=s["category"],
            share_pct=s["share_pct"],
            volume_signal=s["volume_signal"],
            trend="rising" if s["trend"] > 5 else "stable" if s["trend"] >= -5 else "declining",
        )
        for s in shares
    ]

    return CorridorIntelligence(
        source_country=config["source"],
        destination_country=config["destination"],
        dominant_rail=dominant_rail,
        volume_trend=f"{'+' if avg_trend >= 0 else ''}{avg_trend:.1f}% WoW",
        volume_signal=avg_signal,
        volume_change_pct=round(avg_trend, 1),
        congestion_level=cong_level,
        liquidity_signal=liq_signal,
        rail_breakdown=rail_breakdown,
        observed_at=now,
    )


@router.get("/{corridor}/rails/compare", response_model=RailComparison)
async def compare_corridor_rails(
    corridor: str,
    rails: Optional[str] = Query(None, description="Comma-separated rail names to compare"),
):
    """
    Side-by-side comparison of rails on a corridor.
    Mixes categories — compare SWIFT, Wise, M-Pesa, and USDC/Solana on one screen.
    """
    corridor_upper = corridor.upper()
    config = CORRIDOR_RAIL_MAP.get(corridor_upper)

    if not config:
        raise HTTPException(status_code=404, detail=f"Corridor '{corridor}' not found")

    now = datetime.now(timezone.utc).isoformat()

    # Filter to requested rails or return all
    rail_filter = set(rails.split(",")) if rails else None
    corridor_rails = [
        r for r in config["rails"]
        if not rail_filter or r["rail"] in rail_filter
    ]

    comparison_rows = []
    for rail_def in corridor_rails:
        rail_data = get_rail_data(rail_def["rail"])
        if not rail_data:
            continue

        trend = rail_data.get("volume_change_pct", 0)
        comparison_rows.append(RailComparisonRow(
            name=rail_def["rail"],
            category=rail_def["category"],
            volume_index=rail_data.get("volume_index", 50),
            fee_index=rail_data.get("fee_index", 50),
            speed_index=rail_data.get("speed_index", 50),
            congestion_level=rail_data.get("congestion_level", "low"),
            avg_speed=SPEED_MAP.get(rail_def["rail"], "Unknown"),
            volume_signal=rail_data.get("volume_signal", "stable"),
            signal=rail_data.get("signal", ""),
            trend="rising" if trend > 5 else "stable" if trend >= -5 else "declining",
        ))

    comparison_rows.sort(key=lambda r: r.volume_index, reverse=True)

    return RailComparison(
        source_country=config["source"],
        destination_country=config["destination"],
        rails=comparison_rows,
        compared_at=now,
    )


@router.get("")
async def list_corridors():
    """List all supported corridors."""
    return {
        "corridors": [
            {
                "code":        code,
                "source":      config["source"],
                "destination": config["destination"],
                "rail_count":  len(config["rails"]),
            }
            for code, config in CORRIDOR_RAIL_MAP.items()
        ]
    }
