# GFOS — Global Financial Operating System

> **"One dashboard. Every financial rail on earth."**  
> From SWIFT wire transfers to M-Pesa to Bitcoin — see where money is moving, across all of them, at once.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## What is GFOS?

GFOS is an open-source **financial intelligence platform** that unifies observation across every layer of the global financial system into a single intelligence layer and dashboard.

**GFOS does not move money. It watches where money moves — across everything.**

Today, if you want to understand global money flows you need:
- A Bloomberg terminal for banking rails
- A Chainalysis subscription for crypto flows
- A separate tool for mobile money
- Another for remittance apps
- And none of them talk to each other

**GFOS collapses all of that into one system.**

```
GFOS UNIFIED RAIL INTELLIGENCE  |  Live  |  Updated 12s ago
══════════════════════════════════════════════════════════════════════

BANKING RAILS
  SWIFT          Global        ↓  Congestion detected      +2.1% fee surge
  SEPA Instant   EU Internal   →  Stable, deep liquidity   Normal
  ACH            US Internal   →  Stable                   End-of-month volume
  Fedwire        US            ↑  +8% volume               Large corporates active
  CIPS           CN → Global   ↑↑ +61% YTD                 Trade finance expansion
  CHAPS          UK            →  Stable                   Normal

REMITTANCE APPS
  Wise           Global        ↑  +22% volume              GBP/KES corridor surging
  Western Union  Global        ↓  -11% volume              Losing share to mobile
  Remitly        US → LATAM    ↑  +18%                     Post-payday spike
  WorldRemit     UK → Africa   ↑  +31%                     Harvest season inflows

MOBILE MONEY
  M-Pesa         KE / TZ       ↑  +34% volume              Harvest season
  MTN MoMo       West Africa   ↑  +18%                     Post-harvest inflows
  Airtel Money   East Africa   →  Stable                   Normal
  Wave           Senegal/Mali  ↑↑ +47%                     Rapid market expansion
  Orange Money   West Africa   →  Stable                   Normal

CRYPTO NETWORKS
  Solana USDC    Global        ↑↑ Surging                  FX arbitrage signal
  TRON USDT      Global        ↑  +29%                     Remittance substitution
  Stellar XLM    Cross-border  ↑  +15%                     Institutional corridors
  Bitcoin        Global        →  Stable                   Low remittance usage
  Ethereum       Global        ↓  High gas fees            Congestion event

FX MARKETS
  USD/KES        →  1 USD = 129.4 KES   Spread widening signal
  EUR/NGN        ↑  Pressure building   Parallel market divergence
  GBP/GHS        →  Stable              Normal interbank spread
══════════════════════════════════════════════════════════════════════
```

This is what a central bank analyst, a fintech strategist, a remittance operator, or an impact investor has never been able to see in one place. Until now.

---

## The Problem

The global financial system moves **$190 trillion annually**. It runs across four completely separate worlds that have never been unified:

| World | Examples | Current Intelligence |
|-------|----------|---------------------|
| **Banking Rails** | SWIFT, ACH, SEPA, Fedwire, CHAPS, CIPS | Bloomberg (expensive, siloed) |
| **Remittance Apps** | Wise, Western Union, Remitly, WorldRemit | None — completely dark |
| **Mobile Money** | M-Pesa, MTN MoMo, Wave, Airtel | None — completely dark |
| **Crypto Networks** | USDC/Solana, USDT/TRON, Stellar, Bitcoin | Chainalysis (crypto-only) |

**The result:** capital allocation decisions, policy interventions, and product strategies are made with a fraction of the picture.

GFOS is the layer that reads all four worlds simultaneously and makes them comparable.

---

## Core Intelligence Modules

| Module | What It Observes | Rails Covered | Status |
|--------|-----------------|---------------|--------|
| **Banking Rail Monitor** | SWIFT corridors, ACH volumes, wire transfer flow, interbank signals | SWIFT, SEPA, ACH, Fedwire, CHAPS, CIPS, RTGS | 🔨 Building |
| **Remittance App Tracker** | App-level volume trends, corridor share shifts, fee movements | Wise, WU, Remitly, WorldRemit, Sendwave | 🔨 Building |
| **Mobile Money Monitor** | Network flow, corridor dominance, seasonal patterns | M-Pesa, MTN, Airtel, Wave, Orange, GCash | 🔨 Building |
| **Crypto Flow Intelligence** | On-chain volume, stablecoin flows, network congestion | Solana, TRON, Stellar, Bitcoin, Ethereum | 🔨 Building |
| **FX Signal Engine** | Cross-rail FX pressure, spread signals, arbitrage indicators | 170+ currency pairs | 🔨 Building |
| **Congestion Detector** | Bottlenecks and delays across all rail types simultaneously | All rails | 🔨 Building |
| **Liquidity Heatmap** | Where liquidity is concentrating and dispersing globally | All rails | 🔨 Building |
| **Corridor Intelligence** | Which rail dominates any given corridor, and why | All corridors | 🔨 Building |
| **AI Pattern Engine** | Predict rail shifts before they happen | All rails | 📋 Planned |
| **Regulation Pulse** | Corridor policy changes, capital controls, crypto restrictions | All jurisdictions | 📋 Planned |
| **Unified Dashboard** | One screen — every rail, every corridor, every signal | All rails | 📋 Planned |

---

## The Unified Dashboard

GFOS's dashboard is built around one principle: **no switching between tools**.

Every panel lives in a single view:

```
┌─────────────────────────────────────────────────────────────────┐
│  GFOS  |  Global Flow Map  |  Rails  |  Corridors  |  Signals  │
├──────────────────────────┬──────────────────────────────────────┤
│                          │  RAIL PERFORMANCE COMPARISON         │
│   GLOBAL FLOW MAP        │  ─────────────────────────────────── │
│   (Mapbox — live)        │  Rail          Vol    Fee    Speed   │
│                          │  SWIFT         ↓      ↑↑     Slow   │
│   🔴 SWIFT congestion    │  SEPA Instant  →      →      Fast   │
│   🟢 SEPA deep liq.      │  Wise          ↑      →      Fast   │
│   🟡 M-Pesa surging      │  M-Pesa        ↑↑     ↓      Fast   │
│   🔵 USDC flowing        │  USDT/TRON     ↑      ↓↓     Fast   │
│                          │  Remitly       ↑      →      Medium │
├──────────────────────────┴──────────────────────────────────────┤
│  CORRIDOR DEEP DIVE:  Kenya → Germany                           │
│  ─────────────────────────────────────────────────────────────  │
│  Dominant flow:  M-Pesa → USDC/Solana → SEPA  (62% of volume)  │
│  Rising:         Remitly → SWIFT  (+18% this week)              │
│  Declining:      Western Union (–14%, losing share)             │
│  AI Forecast:    "Volume likely to increase — harvest season"   │
├─────────────────────────────────────────────────────────────────┤
│  LIVE SIGNALS                                                   │
│  ⚡ SWIFT AF→EU congestion spike detected  (2 mins ago)        │
│  ⚡ USDT/TRON volume +29% — remittance substitution signal      │
│  ⚡ Wave (Senegal) +47% — fastest-growing mobile rail globally  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
git clone https://github.com/your-org/gfos.git
cd gfos

pip install -r requirements.txt

# Start the intelligence API
uvicorn backend.api.main:app --reload

# Query a corridor across ALL rail types
curl "http://localhost:8000/v1/corridors/KE-DE/intelligence"

# Compare all rails on a corridor
curl "http://localhost:8000/v1/corridors/KE-DE/rails/compare"

# Global heatmap snapshot
curl "http://localhost:8000/v1/heatmap/snapshot"

# Which rails are surging right now, across all categories?
curl "http://localhost:8000/v1/rails/surging?threshold=0.15"
```

---

## SDK Usage

### Python

```python
from gfos import GFOSClient

client = GFOSClient(api_key="your_key")

# ── Corridor Intelligence (cross-rail) ───────────────────────────

intel = client.corridor("KE", "DE")

print(intel.dominant_rail)      # "M-Pesa → USDC/Solana → SEPA"
print(intel.volume_trend)       # "+34% WoW"
print(intel.rail_breakdown)
# [
#   RailShare(rail="M-Pesa→USDC→SEPA",  share=0.62, trend="rising"),
#   RailShare(rail="Remitly→SWIFT",      share=0.21, trend="rising"),
#   RailShare(rail="Western Union",      share=0.17, trend="declining"),
# ]

# ── Compare Rails Side-by-Side ───────────────────────────────────

comparison = client.compare(
    source="KE",
    destination="DE",
    rails=["SWIFT", "Wise", "M-Pesa", "USDC/Solana", "Western Union"]
)

for rail in comparison.rails:
    print(f"{rail.name:20} vol:{rail.volume_index:.2f}  fee:{rail.fee_index:.2f}  speed:{rail.avg_speed}")

# SWIFT               vol:0.21  fee:0.89  speed:2-5 days
# Wise                vol:0.34  fee:0.31  speed:~2 hours
# M-Pesa              vol:0.62  fee:0.08  speed:~10 seconds
# USDC/Solana         vol:0.58  fee:0.03  speed:~5 seconds
# Western Union       vol:0.17  fee:0.72  speed:minutes-hours

# ── Surging Rails (all categories) ───────────────────────────────

surging = client.rails.surging(threshold=0.15)
for rail in surging:
    print(rail.name, rail.category, rail.volume_change_pct, rail.signal)

# Wave             mobile_money   +47%   fastest-growing mobile rail
# USDT/TRON        crypto         +29%   remittance substitution
# CIPS             banking        +61%   trade finance expansion
# Remitly          remittance     +18%   post-payday US→LATAM spike

# ── Banking Rail Intelligence ─────────────────────────────────────

swift = client.rails.get("SWIFT")
print(swift.congestion_level)   # "high"
print(swift.signal)             # "AF→EU corridor under pressure"
print(swift.fee_trend)          # "+2.1% this week"

# ── Crypto Flow Intelligence ──────────────────────────────────────

usdt_tron = client.rails.get("USDT/TRON")
print(usdt_tron.volume_change_pct)   # 29.4
print(usdt_tron.signal)              # "remittance substitution — informal corridor growth"

# ── Live Stream (all rails, all categories) ───────────────────────

stream = client.stream.all()
stream.on("update", lambda u: print(f"[{u.category}] {u.rail}: {u.signal}"))
```

### TypeScript

```typescript
import { GFOSClient } from '@gfos/sdk';

const client = new GFOSClient({ apiKey: 'your_key' });

// Full corridor picture — all rails compared
const intel = await client.corridor('KE', 'DE');
console.log(intel.dominantRail);    // 'M-Pesa → USDC/Solana → SEPA'
console.log(intel.railBreakdown);   // array of RailShare objects

// Side-by-side comparison
const comparison = await client.compare({
  source: 'KE',
  destination: 'DE',
  rails: ['SWIFT', 'Wise', 'M-Pesa', 'USDC/Solana'],
});

comparison.rails.forEach(r => {
  console.log(r.name, r.volumeIndex, r.feeIndex, r.avgSpeed);
});

// Stream all rails live
const stream = client.stream.all();
stream.on('update', (update) => {
  console.log(`[${update.category}] ${update.rail}: ${update.signal}`);
});
```

---

## Full Rail Coverage

### 🏦 Banking Rails
| Rail | Region | Coverage |
|------|--------|----------|
| SWIFT | Global | Cross-border wire intelligence |
| SEPA / SEPA Instant | EU | EUR corridor flows |
| ACH | United States | Domestic batch transfer volumes |
| Fedwire | United States | Large-value wire signals |
| CHAPS | United Kingdom | GBP high-value flows |
| CIPS | China / Global | CNY cross-border expansion signals |
| RTGS systems | 80+ countries | Central bank settlement indicators |
| IMPS / UPI | India | Domestic + diaspora corridor signals |

### 💸 Remittance Apps
| App | Key Corridors | Coverage |
|-----|--------------|----------|
| Wise (TransferWise) | Global | Volume, fee trends, corridor shifts |
| Western Union | Global | Market share, corridor performance |
| Remitly | US → LATAM, Asia | Volume spikes, corridor dominance |
| WorldRemit | UK, EU → Africa | African corridor intelligence |
| Sendwave | US, UK → Africa | Mobile-first remittance signals |
| MoneyGram | Global | Agent network load signals |
| Paysend | EU → CIS | Eastern Europe corridor signals |

### 📱 Mobile Money
| Network | Markets | Coverage |
|---------|---------|----------|
| M-Pesa | Kenya, Tanzania, Ethiopia | Volume, congestion, seasonal patterns |
| MTN MoMo | 18 African markets | West/Central Africa flow intelligence |
| Airtel Money | East/Central Africa | Regional corridor signals |
| Wave | Senegal, Mali, Côte d'Ivoire | Fastest-growing mobile rail signals |
| Orange Money | West/Central Africa | Francophone corridor flows |
| GCash | Philippines | Diaspora remittance signals |
| bKash | Bangladesh | Garment worker remittance corridor |
| Easypaisa | Pakistan | South Asian corridor intelligence |

### ₿ Crypto Networks
| Network | Asset | Coverage |
|---------|-------|----------|
| Solana | USDC | Stablecoin remittance flows, speed signals |
| TRON | USDT | Largest stablecoin transfer network by volume |
| Stellar | XLM | Institutional and development corridor flows |
| Ethereum | USDC, USDT | On-chain volume, gas congestion signals |
| Bitcoin | BTC | Store-of-value vs remittance usage signal |
| Lightning Network | BTC | Micro-payment and remittance rail signals |

### 💹 FX Markets
- 170+ live currency pairs
- Cross-rail FX pressure detection
- Parallel market divergence signals (where official vs market rates diverge)
- Spread widening as liquidity stress indicator

---

## Architecture

```
DATA SOURCES (read-only observation)
  Banking APIs    Remittance App APIs    Mobile Money APIs
  Crypto RPCs     FX Feeds               Central Bank Data
  Community Observations
                          ↓
DATA COLLECTORS (Python — inbound only)
  Scheduled polling · Webhook receivers · Health probes
                          ↓
STREAMING LAYER (Kafka / Redis)
  Real-time ingestion · Pattern triggers · Cross-rail alerts
                          ↓
DATABASE LAYER
  PostgreSQL (time-series metrics)
  Neo4j (unified rail graph — all categories)
                          ↓
INTELLIGENCE LAYER
  Flow Analysis · Congestion Detector · Liquidity Modeller
  Cross-Rail Comparator · AI Pattern Engine · Regulation Pulse
                          ↓
API LAYER (FastAPI — read-only)
  REST + WebSocket
                          ↓
UNIFIED DASHBOARD (Next.js + Mapbox + D3.js)
  Global Flow Map · Rail Comparison Panel · Corridor Deep Dive
  Liquidity Heatmap · Live Signal Feed
```

Full detail: [`docs/architecture.md`](docs/architecture.md)

---

## Who Uses This Intelligence

**Central Banks & Regulators** — the first unified view of capital flows across banking, mobile money, remittance, and crypto simultaneously. Essential for FX intervention, capital flow monitoring, and financial inclusion policy.

**Fintechs & Remittance Operators** — see how your corridor is moving before your users feel it. Monitor competitors across categories, not just your own rail type.

**Impact Investors & Development Finance** — understand where capital is actually flowing in emerging markets. Identify underserved corridors with intelligence, not anecdote.

**Trade Finance Desks** — spot cross-border volume shifts early. CIPS expansion, SWIFT congestion, and crypto rail growth all signal the same underlying trade flow changes.

**Hedge Funds & Macro Analysts** — remittance flow data is one of the best leading indicators of economic activity in emerging markets. GFOS makes it machine-readable.

**Researchers & Journalists** — the first open, unified dataset of global money flow across all rail categories.

---

## Development Roadmap

```
Phase 1 — Core Intelligence Engine + Banking Rail Observers     ← We are here
Phase 2 — Remittance App + Mobile Money + Crypto Observers
Phase 3 — Cross-Rail Comparison Engine + Corridor Intelligence
Phase 4 — AI Pattern + Forecasting Engine
Phase 5 — Unified Global Dashboard (Mapbox + D3.js)
Phase 6 — Institutional API (subscription tier)
```

---

## Contributing

We need observers for every rail category. If you know a rail, connect it.

- **Banking** — SWIFT, ACH, SEPA, RTGS, CIPS, UPI integrations
- **Remittance** — Wise, WU, Remitly, WorldRemit API observers
- **Mobile money** — MTN MoMo, Wave, GCash, bKash, Easypaisa
- **Crypto** — TRON, Stellar, Lightning Network, Ethereum observers
- **FX** — central bank feeds, parallel market signals
- **ML / AI** — time-series forecasting, pattern detection
- **Frontend** — Next.js dashboard, Mapbox visualisation, D3.js panels
- **Domain experts** — rail knowledge, corridor analysis, compliance

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) — look for `good first issue` tags.

---

## For Investors & Partners

GFOS is building the intelligence layer the $190 trillion global payments market has never had — unified across every rail category for the first time.

- **Zero payment liability** — we observe and report, we never touch money
- **No money transmission licence required** — pure intelligence platform
- **Emerging market first** — mobile money and African corridors are day-one priorities
- **Subscription + API model** — Bloomberg-style institutional access, open data for developers
- **Community-powered data** — rail observers contributed by a global developer community

Reach out via [Discussions](../../discussions).

---

## License

MIT — free to use, modify, and build upon.

---

<p align="center">
  <strong>Every bank. Every app. Every network. Every rail.<br/>
  One dashboard. One intelligence layer. One picture of where money moves.</strong>
  <br/><br/>
  Built for the world. Starting from Africa.
</p>
