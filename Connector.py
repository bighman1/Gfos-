"""
GFOS Plugin: M-Pesa Observer
Read-only intelligence observer for the M-Pesa payment rail.

This observer connects GFOS to M-Pesa status and volume signals.
It does NOT initiate, authorise, or process payments.

Observed corridors:
  - Kenya internal (KES)
  - Kenya → Tanzania (cross-border signal)
  - Kenya → inbound remittance (GlobalPay volume indicators)
"""

from __future__ import annotations
import os
import httpx
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class MPesaObservation:
    """Intelligence snapshot from the M-Pesa rail at a point in time."""
    rail: str = "M-Pesa"
    rail_type: str = "mobile_money"
    volume_index: float = 0.0        # 0–1, relative to rail's own baseline
    fee_index: float = 0.0           # 0–1, relative to baseline (higher = more expensive)
    congestion_score: float = 0.0    # 0–1 (higher = more congested)
    liquidity_score: float = 0.0     # 0–1 (higher = deeper liquidity)
    signal: str = "stable"           # human-readable signal note
    active_corridors: List[str] = None
    observed_at: str = ""

    def __post_init__(self):
        if self.active_corridors is None:
            self.active_corridors = []


class MPesaObserver:
    """
    GFOS read-only observer for M-Pesa.

    Observes M-Pesa rail health and flow signals by querying
    Safaricom's developer APIs for status data.

    This class never initiates transactions.
    It only reads status, health, and publicly observable metrics.

    Configuration (env vars):
        MPESA_CONSUMER_KEY     — read-only API key from Safaricom developer portal
        MPESA_CONSUMER_SECRET
        MPESA_ENV              — "sandbox" | "production"
    """

    RAIL_ID   = "M-Pesa"
    RAIL_TYPE = "mobile_money"
    CURRENCY  = "KES"

    SANDBOX_BASE    = "https://sandbox.safaricom.co.ke"
    PRODUCTION_BASE = "https://api.safaricom.co.ke"

    def __init__(
        self,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        env: str = "sandbox",
    ):
        self.consumer_key    = consumer_key    or os.environ.get("MPESA_CONSUMER_KEY", "")
        self.consumer_secret = consumer_secret or os.environ.get("MPESA_CONSUMER_SECRET", "")
        self.base_url        = self.SANDBOX_BASE if env == "sandbox" else self.PRODUCTION_BASE
        self._token: Optional[str] = None

    # ── GFOS Observer Interface ───────────────

    def rail_metadata(self) -> dict:
        """Returns rail metadata for registration in the GFOS payment graph."""
        return {
            "rail_id":   self.RAIL_ID,
            "rail_type": self.RAIL_TYPE,
            "currency":  self.CURRENCY,
            "countries": ["KE", "TZ"],
            "description": "Safaricom M-Pesa mobile money network",
            "data_coverage": ["volume_index", "fee_index", "congestion_score"],
        }

    def observe(self) -> MPesaObservation:
        """
        Pull current observable metrics from the M-Pesa rail.
        READ ONLY — never initiates transactions.
        """
        import datetime
        health = self._fetch_health_signal()
        return MPesaObservation(
            rail=self.RAIL_ID,
            rail_type=self.RAIL_TYPE,
            volume_index=health.get("volume_index", 0.65),
            fee_index=health.get("fee_index", 0.30),
            congestion_score=health.get("congestion_score", 0.08),
            liquidity_score=health.get("liquidity_score", 0.82),
            signal=health.get("signal", "stable"),
            active_corridors=["KE-TZ", "KE-UG", "KE-ET", "KE-RW"],
            observed_at=datetime.datetime.utcnow().isoformat() + "Z",
        )

    # ── Internal ──────────────────────────────

    def _fetch_health_signal(self) -> dict:
        """Placeholder: returns synthetic baseline metrics. Phase 2: live API."""
        return {
            "volume_index":     0.65,
            "fee_index":        0.30,
            "congestion_score": 0.08,
            "liquidity_score":  0.82,
            "signal":           "stable",
        }

    def _get_token(self) -> str:
        """Obtain OAuth2 token for Safaricom API (read-only credential)."""
        if self._token:
            return self._token
        import base64
        credentials = base64.b64encode(
            f"{self.consumer_key}:{self.consumer_secret}".encode()
        ).decode()
        with httpx.Client(base_url=self.base_url) as client:
            resp = client.get(
                "/oauth/v1/generate?grant_type=client_credentials",
                headers={"Authorization": f"Basic {credentials}"},
                timeout=15,
            )
            resp.raise_for_status()
            self._token = resp.json()["access_token"]
        return self._token
