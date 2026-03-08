"""
GFOS Data Models
All API response shapes defined here.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum


class RailCategory(str, Enum):
    BANKING      = "banking"
    REMITTANCE   = "remittance"
    MOBILE_MONEY = "mobile_money"
    CRYPTO       = "crypto"
    FX           = "fx"


class VolumeSignal(str, Enum):
    SURGING   = "surging"
    RISING    = "rising"
    STABLE    = "stable"
    DECLINING = "declining"
    DRAINING  = "draining"


class CongestionLevel(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


class LiquiditySignal(str, Enum):
    DEEP     = "deep"
    MODERATE = "moderate"
    SHALLOW  = "shallow"
    DRY      = "dry"


class RailIntelligence(BaseModel):
    rail: str
    category: RailCategory
    volume_index: float          # 0–100 normalised
    volume_change_pct: float     # WoW change
    volume_signal: VolumeSignal
    fee_index: float             # 0–100 (lower = cheaper)
    fee_trend: str
    speed_index: float           # 0–100 (higher = faster)
    congestion_score: float      # 0–100 (higher = more congested)
    congestion_level: CongestionLevel
    liquidity_signal: LiquiditySignal
    active_corridors: List[str]
    signal: str                  # analyst note
    observed_at: str


class RailShare(BaseModel):
    rail: str
    category: RailCategory
    share_pct: float
    volume_signal: VolumeSignal
    trend: str


class CorridorIntelligence(BaseModel):
    source_country: str
    destination_country: str
    dominant_rail: str
    volume_trend: str
    volume_signal: VolumeSignal
    volume_change_pct: float
    congestion_level: CongestionLevel
    liquidity_signal: LiquiditySignal
    rail_breakdown: List[RailShare]
    ai_forecast: Optional[str] = None
    observed_at: str


class RailComparisonRow(BaseModel):
    name: str
    category: RailCategory
    volume_index: float
    fee_index: float
    speed_index: float
    congestion_level: CongestionLevel
    avg_speed: str
    volume_signal: VolumeSignal
    signal: str
    trend: str


class RailComparison(BaseModel):
    source_country: str
    destination_country: str
    rails: List[RailComparisonRow]
    compared_at: str


class HeatmapEntry(BaseModel):
    corridor: str
    intensity: float


class HeatmapShift(BaseModel):
    corridor: str
    change_pct: float
    direction: str


class HeatmapSnapshot(BaseModel):
    hotspots: List[HeatmapEntry]
    cold_zones: List[HeatmapEntry]
    shifts: List[HeatmapShift]
    by_category: Dict[str, List[HeatmapEntry]]
    generated_at: str


class FXSignal(BaseModel):
    pair: str
    rate: float
    spread_signal: str
    parallel_market_divergence: Optional[float] = None
    cross_rail_pressure: str
    source: str
    observed_at: str


class FXRates(BaseModel):
    base: str
    rates: Dict[str, float]
    observed_at: str
