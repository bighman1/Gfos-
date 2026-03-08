"""
GFOS Python SDK
Global Financial Operating System — Unified Rail Intelligence Client

GFOS observes and surfaces intelligence across every financial rail category:
  - Banking rails (SWIFT, SEPA, ACH, Fedwire, CHAPS, CIPS, RTGS, UPI)
  - Remittance apps (Wise, Western Union, Remitly, WorldRemit, Sendwave)
  - Mobile money (M-Pesa, MTN MoMo, Wave, Airtel, Orange, GCash, bKash)
  - Crypto networks (Solana/USDC, TRON/USDT, Stellar, Bitcoin, Ethereum)
  - FX markets (170+ currency pairs, cross-rail pressure signals)

GFOS does not process payments. It watches where money moves — across all of them.

pip install gfos-sdk
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import httpx


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────

class RailCategory(str, Enum):
    BANKING      = "banking"       # SWIFT, SEPA, ACH, Fedwire, CHAPS, CIPS
    REMITTANCE   = "remittance"    # Wise, Western Union, Remitly, WorldRemit
    MOBILE_MONEY = "mobile_money"  # M-Pesa, MTN MoMo, Wave, Airtel, GCash
    CRYPTO       = "crypto"        # Solana, TRON, Stellar, Bitcoin, Ethereum
    FX           = "fx"            # Currency pairs, FX market signals


class CongestionLevel(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


class LiquiditySignal(str, Enum):
    DEEP     = "deep"
    MODERATE = "moderate"
    SHALLOW  = "shallow"
    DRY      = "dry"


class VolumeSignal(str, Enum):
    SURGING   = "surging"    # +30%+
    RISING    = "rising"     # +10–30%
    STABLE    = "stable"     # ±10%
    DECLINING = "declining"  # -10–30%
    DRAINING  = "draining"   # -30%+


# ─────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────

@dataclass
class RailShare:
    """
    A single rail's share of flow on a corridor.
    Part of corridor breakdown — shows which rails dominate and which are declining.
    """
    rail: str
    category: RailCategory
    share_pct: float         # percentage of corridor volume on this rail
    volume_signal: VolumeSignal
    trend: str               # "rising" | "stable" | "declining"


@dataclass
class RailComparison:
    """
    Side-by-side comparison of multiple rails on a corridor.
    The core output of client.compare() — lets you see all rails simultaneously.

    Example:
        comparison = client.compare("KE", "DE", ["SWIFT", "Wise", "M-Pesa", "USDC/Solana"])

        for rail in comparison.rails:
            print(f"{rail.name:20}  vol:{rail.volume_index:.2f}  fee:{rail.fee_index:.2f}  {rail.avg_speed}")

        # SWIFT               vol:0.21  fee:0.89  2-5 days
        # Wise                vol:0.34  fee:0.31  ~2 hours
        # M-Pesa              vol:0.62  fee:0.08  ~10 seconds
        # USDC/Solana         vol:0.58  fee:0.03  ~5 seconds
    """
    source_country: str
    destination_country: str
    rails: List["RailComparisonRow"]
    compared_at: str


@dataclass
class RailComparisonRow:
    """A single rail row in a cross-rail comparison."""
    name: str
    category: RailCategory
    volume_index: float      # 0–1, normalised to corridor baseline
    fee_index: float         # 0–1 (lower = cheaper relative to corridor)
    congestion_level: CongestionLevel
    avg_speed: str           # human-readable e.g. "~10 seconds", "2-5 days"
    volume_signal: VolumeSignal
    signal: str              # analyst note
    trend: str               # "rising" | "stable" | "declining"


@dataclass
class CorridorIntelligence:
    """
    Full intelligence snapshot for a payment corridor across ALL rail categories.

    Example:
        intel = client.corridor("KE", "DE")
        intel.dominant_rail      → "M-Pesa → USDC/Solana → SEPA"
        intel.volume_trend       → "+34% WoW"
        intel.rail_breakdown     → [RailShare, RailShare, ...]   # all rails ranked
        intel.ai_forecast        → "Volume likely to increase — harvest season"
    """
    source_country: str
    destination_country: str
    dominant_rail: str
    volume_trend: str
    volume_signal: VolumeSignal
    volume_change_pct: float
    congestion_level: CongestionLevel
    liquidity_signal: LiquiditySignal
    rail_breakdown: List[RailShare]   # all observed rails ranked by share
    ai_forecast: Optional[str]
    observed_at: str


@dataclass
class RailIntelligence:
    """
    Live intelligence for a single rail, regardless of category.

    Works identically whether the rail is SWIFT, Wise, M-Pesa, or Solana.

    Example:
        swift  = client.rails.get("SWIFT")
        mpesa  = client.rails.get("M-Pesa")
        usdt   = client.rails.get("USDT/TRON")
        wise   = client.rails.get("Wise")
    """
    rail: str
    category: RailCategory
    volume_change_pct: float
    volume_signal: VolumeSignal
    congestion_level: CongestionLevel
    liquidity_signal: LiquiditySignal
    fee_trend: str            # e.g. "+2.1% this week", "Stable", "Declining"
    active_corridors: List[str]
    signal: str               # analyst-style note
    observed_at: str


@dataclass
class HeatmapSnapshot:
    """
    Global liquidity heatmap across ALL rail categories.

    Shows where financial liquidity is concentrating and dispersing
    across the entire global financial system simultaneously.
    """
    hotspots: List[dict]    # highest liquidity concentration
    cold_zones: List[dict]  # emerging liquidity gaps
    shifts: List[dict]      # corridors with >20% liquidity shift in 24h
    by_category: Dict[str, List[dict]]  # breakdown per rail category
    generated_at: str


@dataclass
class RailHistory:
    """Historical flow data for any rail over a time window."""
    rail: str
    category: RailCategory
    days: int
    peak_days: List[str]
    peak_hours: List[int]
    avg_volume_index: float
    correlation: Dict[str, float]   # correlation with other rails (cross-category)
    seasonality: Optional[str]
    data_points: int


@dataclass
class FXSignal:
    """
    FX market intelligence for a currency pair.
    Includes cross-rail pressure signals — when FX stress shows up differently
    on banking rails vs parallel markets vs crypto rails.
    """
    pair: str                      # e.g. "USD/KES"
    rate: float
    spread_signal: str             # "normal" | "widening" | "stressed"
    parallel_market_divergence: Optional[float]  # % gap from official rate
    cross_rail_pressure: str       # which rail category is absorbing FX pressure
    observed_at: str


# ─────────────────────────────────────────────
# Sub-clients
# ─────────────────────────────────────────────

class RailsClient:
    """Access intelligence on any individual rail — banking, remittance, mobile, crypto."""

    def __init__(self, http: httpx.Client):
        self._http = http

    def get(self, rail: str) -> RailIntelligence:
        """
        Get live intelligence for any rail by name.

        Works for any category:
            client.rails.get("SWIFT")        # banking
            client.rails.get("Wise")         # remittance
            client.rails.get("M-Pesa")       # mobile money
            client.rails.get("USDT/TRON")    # crypto
        """
        resp = self._http.get(f"/rails/{rail}/intelligence")
        resp.raise_for_status()
        return self._parse(resp.json())

    def surging(
        self,
        threshold: float = 0.15,
        categories: Optional[List[RailCategory]] = None,
    ) -> List[RailIntelligence]:
        """
        Returns rails with volume surges above threshold — across all categories.

        Args:
            threshold:  Minimum volume change (0.15 = 15% increase)
            categories: Optional filter by category (default: all categories)

        Example:
            surging = client.rails.surging(threshold=0.15)
            for rail in surging:
                print(rail.rail, rail.category, rail.volume_change_pct, rail.signal)

            # Wave             mobile_money   +47%   fastest-growing mobile rail
            # USDT/TRON        crypto         +29%   remittance substitution
            # CIPS             banking        +61%   trade finance expansion
            # Remitly          remittance     +18%   post-payday spike
        """
        params: dict = {"threshold": threshold}
        if categories:
            params["categories"] = ",".join(c.value for c in categories)
        resp = self._http.get("/rails/surging", params=params)
        resp.raise_for_status()
        return [self._parse(r) for r in resp.json()["rails"]]

    def congested(self) -> List[RailIntelligence]:
        """Rails with detected congestion — across all categories."""
        resp = self._http.get("/rails/congested")
        resp.raise_for_status()
        return [self._parse(r) for r in resp.json()["rails"]]

    def by_category(self, category: RailCategory) -> List[RailIntelligence]:
        """
        Get all observed rails in a specific category.

        Example:
            banking_rails    = client.rails.by_category(RailCategory.BANKING)
            remittance_rails = client.rails.by_category(RailCategory.REMITTANCE)
            mobile_rails     = client.rails.by_category(RailCategory.MOBILE_MONEY)
            crypto_rails     = client.rails.by_category(RailCategory.CRYPTO)
        """
        resp = self._http.get(f"/rails/category/{category.value}")
        resp.raise_for_status()
        return [self._parse(r) for r in resp.json()["rails"]]

    def history(self, rail: str, days: int = 30) -> RailHistory:
        """Historical flow data for any rail. Lookback up to 365 days."""
        resp = self._http.get(f"/rails/{rail}/history", params={"days": days})
        resp.raise_for_status()
        d = resp.json()
        return RailHistory(
            rail=d["rail"],
            category=RailCategory(d["category"]),
            days=d["days"],
            peak_days=d["peak_days"],
            peak_hours=d["peak_hours"],
            avg_volume_index=d["avg_volume_index"],
            correlation=d["correlation"],
            seasonality=d.get("seasonality"),
            data_points=d["data_points"],
        )

    def _parse(self, d: dict) -> RailIntelligence:
        return RailIntelligence(
            rail=d["rail"],
            category=RailCategory(d["category"]),
            volume_change_pct=d["volume_change_pct"],
            volume_signal=VolumeSignal(d["volume_signal"]),
            congestion_level=CongestionLevel(d["congestion_level"]),
            liquidity_signal=LiquiditySignal(d["liquidity_signal"]),
            fee_trend=d["fee_trend"],
            active_corridors=d["active_corridors"],
            signal=d["signal"],
            observed_at=d["observed_at"],
        )


class HeatmapClient:
    """Global liquidity heatmap — all rail categories."""

    def __init__(self, http: httpx.Client):
        self._http = http

    def snapshot(self) -> HeatmapSnapshot:
        """
        Current global liquidity heatmap across all rail categories.
        Shows hotspots, cold zones, and significant 24h shifts.
        """
        resp = self._http.get("/heatmap/snapshot")
        resp.raise_for_status()
        d = resp.json()
        return HeatmapSnapshot(
            hotspots=d["hotspots"],
            cold_zones=d["cold_zones"],
            shifts=d["shifts"],
            by_category=d["by_category"],
            generated_at=d["generated_at"],
        )


class FXClient:
    """FX market intelligence — cross-rail pressure signals."""

    def __init__(self, http: httpx.Client):
        self._http = http

    def signal(self, pair: str) -> FXSignal:
        """
        FX intelligence for a currency pair.
        Includes cross-rail pressure detection — where is FX stress appearing?

        Example:
            signal = client.fx.signal("USD/KES")
            print(signal.spread_signal)              # "widening"
            print(signal.parallel_market_divergence) # 4.2 (% above official)
            print(signal.cross_rail_pressure)        # "crypto rails absorbing informal demand"
        """
        resp = self._http.get(f"/fx/{pair}/signal")
        resp.raise_for_status()
        d = resp.json()
        return FXSignal(
            pair=d["pair"],
            rate=d["rate"],
            spread_signal=d["spread_signal"],
            parallel_market_divergence=d.get("parallel_market_divergence"),
            cross_rail_pressure=d["cross_rail_pressure"],
            observed_at=d["observed_at"],
        )


class StreamClient:
    """WebSocket streaming — real-time updates across all rail categories."""

    def __init__(self, base_url: str, api_key: str):
        self._ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://")
        self._api_key = api_key

    def all(self):
        """Stream live updates from all rails, all categories."""
        from .stream import StreamSubscription
        return StreamSubscription(
            url=f"{self._ws_url}/v1/stream/rails/all",
            api_key=self._api_key,
        )

    def rails(self, rail_ids: List[str]):
        """Stream live updates for specific rails."""
        from .stream import StreamSubscription
        return StreamSubscription(
            url=f"{self._ws_url}/v1/stream/rails",
            api_key=self._api_key,
            rail_ids=rail_ids,
        )

    def category(self, category: RailCategory):
        """Stream all rails within a specific category."""
        from .stream import StreamSubscription
        return StreamSubscription(
            url=f"{self._ws_url}/v1/stream/category/{category.value}",
            api_key=self._api_key,
        )


# ─────────────────────────────────────────────
# Main Client
# ─────────────────────────────────────────────

class GFOSClient:
    """
    GFOS Python SDK — Unified Rail Intelligence Client.

    Observes every financial rail category from a single client:
      Banking · Remittance Apps · Mobile Money · Crypto · FX

    GFOS does not process payments. It watches where money moves.

    Usage:
        from gfos import GFOSClient

        client = GFOSClient(api_key="gfos_live_...")

        # Full corridor picture across all rails
        intel = client.corridor("KE", "DE")

        # Side-by-side rail comparison
        comparison = client.compare("KE", "DE", ["SWIFT", "Wise", "M-Pesa", "USDC/Solana"])

        # Surging rails across all categories
        for rail in client.rails.surging(threshold=0.15):
            print(rail.rail, rail.category, rail.signal)

        # FX pressure signal
        signal = client.fx.signal("USD/KES")
    """

    BASE_URL = "https://api.gfos.io/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.api_key  = api_key or os.environ.get("GFOS_API_KEY")
        if not self.api_key:
            raise ValueError("No API key. Pass api_key= or set GFOS_API_KEY env var.")
        self.base_url = base_url or self.BASE_URL
        self._http = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-SDK-Version": "0.1.0",
            },
            timeout=timeout,
        )
        self.rails   = RailsClient(self._http)
        self.heatmap = HeatmapClient(self._http)
        self.fx      = FXClient(self._http)
        self.stream  = StreamClient(self.base_url, self.api_key)

    # ── Corridor Intelligence ─────────────────

    def corridor(self, source: str, destination: str, period: str = "7d") -> CorridorIntelligence:
        """
        Full intelligence snapshot for a corridor — across ALL rail categories.

        Returns dominant rail, volume trend, full rail breakdown (all categories ranked),
        and AI forecast.

        Args:
            source:      ISO 3166-1 alpha-2 (e.g. "KE")
            destination: ISO 3166-1 alpha-2 (e.g. "DE")
            period:      Comparison period "1d" | "7d" | "30d"
        """
        resp = self._http.get(
            f"/corridors/{source}-{destination}/intelligence",
            params={"period": period},
        )
        resp.raise_for_status()
        d = resp.json()
        return CorridorIntelligence(
            source_country=d["source_country"],
            destination_country=d["destination_country"],
            dominant_rail=d["dominant_rail"],
            volume_trend=d["volume_trend"],
            volume_signal=VolumeSignal(d["volume_signal"]),
            volume_change_pct=d["volume_change_pct"],
            congestion_level=CongestionLevel(d["congestion_level"]),
            liquidity_signal=LiquiditySignal(d["liquidity_signal"]),
            rail_breakdown=[
                RailShare(
                    rail=r["rail"],
                    category=RailCategory(r["category"]),
                    share_pct=r["share_pct"],
                    volume_signal=VolumeSignal(r["volume_signal"]),
                    trend=r["trend"],
                )
                for r in d["rail_breakdown"]
            ],
            ai_forecast=d.get("ai_forecast"),
            observed_at=d["observed_at"],
        )

    # ── Cross-Rail Comparison ─────────────────

    def compare(
        self,
        source: str,
        destination: str,
        rails: Optional[List[str]] = None,
    ) -> RailComparison:
        """
        Compare rails side-by-side on a corridor.
        Can mix rail categories — compare SWIFT, Wise, M-Pesa, and USDC/Solana
        on the same corridor simultaneously.

        Args:
            source:      ISO 3166-1 alpha-2
            destination: ISO 3166-1 alpha-2
            rails:       Optional list of rail names. Default: all observed rails.

        Example:
            comparison = client.compare("KE", "DE")
            for rail in comparison.rails:
                print(f"{rail.name:20}  {rail.volume_index:.2f}  {rail.fee_index:.2f}  {rail.avg_speed}")

            # SWIFT               0.21  0.89  2-5 days
            # Wise                0.34  0.31  ~2 hours
            # M-Pesa              0.62  0.08  ~10 seconds
            # USDC/Solana         0.58  0.03  ~5 seconds
            # Western Union       0.17  0.72  minutes-hours
        """
        params: dict = {}
        if rails:
            params["rails"] = ",".join(rails)
        resp = self._http.get(
            f"/corridors/{source}-{destination}/rails/compare",
            params=params,
        )
        resp.raise_for_status()
        d = resp.json()
        return RailComparison(
            source_country=d["source_country"],
            destination_country=d["destination_country"],
            rails=[
                RailComparisonRow(
                    name=r["name"],
                    category=RailCategory(r["category"]),
                    volume_index=r["volume_index"],
                    fee_index=r["fee_index"],
                    congestion_level=CongestionLevel(r["congestion_level"]),
                    avg_speed=r["avg_speed"],
                    volume_signal=VolumeSignal(r["volume_signal"]),
                    signal=r["signal"],
                    trend=r["trend"],
                )
                for r in d["rails"]
            ],
            compared_at=d["compared_at"],
        )

    # ── Community Observation ─────────────────

    def report_observation(
        self,
        rail: str,
        source: str,
        destination: str,
        congestion_observed: bool,
        fee_index: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> dict:
        """Submit a rail observation to the GFOS community intelligence layer."""
        resp = self._http.post("/report-observation", json={
            "rail": rail,
            "source": source,
            "destination": destination,
            "congestion_observed": congestion_observed,
            "fee_index": fee_index,
            "notes": notes,
        })
        resp.raise_for_status()
        return resp.json()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._http.close()
