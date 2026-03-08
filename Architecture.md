

GFOS Architecture

Core Principle

GFOS is a unified intelligence layer across the entire global financial system.

It observes every rail category simultaneously — banking, remittance apps, mobile money, crypto networks, and FX markets — and makes them comparable in a single system. It does not process, route, or touch payments at any point.

No other system does this. Bloomberg covers banking rails. Chainalysis covers crypto. No tool covers mobile money or remittance apps at all. GFOS collapses all four worlds into one intelligence layer.

The Four Worlds GFOS Unifies

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  BANKING RAILS  │  │ REMITTANCE APPS │  │  MOBILE MONEY   │  │ CRYPTO NETWORKS │
│                 │  │                 │  │                 │  │                 │
│ SWIFT           │  │ Wise            │  │ M-Pesa          │  │ Solana/USDC     │
│ SEPA            │  │ Western Union   │  │ MTN MoMo        │  │ TRON/USDT       │
│ ACH             │  │ Remitly         │  │ Wave            │  │ Stellar/XLM     │
│ Fedwire         │  │ WorldRemit      │  │ Airtel Money    │  │ Bitcoin         │
│ CHAPS           │  │ Sendwave        │  │ Orange Money    │  │ Ethereum        │
│ CIPS            │  │ MoneyGram       │  │ GCash           │  │ Lightning       │
│ RTGS (80+)      │  │ Paysend         │  │ bKash           │  │                 │
│ UPI / IMPS      │  │                 │  │ Easypaisa       │  │                 │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         └───────────────────┴─────────────────────┴────────────────────┘
                                        │
                              ┌─────────▼─────────┐
                              │   GFOS UNIFIED    │
                              │ INTELLIGENCE LAYER│
                              └───────────────────┘

System Diagram

DATA SOURCES
  Banking APIs · Remittance App APIs · Mobile Money APIs
  Crypto RPCs · FX Rate Feeds · Central Bank Data
  Community Observations (POST /report-observation)
  Synthetic Monitoring Agents (read-only health probes)
          ↓
DATA COLLECTORS
  Category-specific Python observers (all read-only)
  Banking Observer · Remittance Observer · Mobile Observer
  Crypto Observer · FX Collector
  Scheduled polling + webhook receivers + health probes
          ↓
STREAMING LAYER
  Apache Kafka / Redis Streams
  Cross-category event ingestion · pattern triggers · alerts
          ↓
DATABASE LAYER
  PostgreSQL — time-series metrics, flow history, FX rates
  Neo4j — unified rail graph (all 4 categories, one graph)
          ↓
INTELLIGENCE LAYER
  Flow Analysis Engine · Congestion Detector
  Cross-Rail Comparator · Liquidity Modeller
  AI Pattern Engine · Regulation Pulse Tracker
          ↓
API LAYER
  FastAPI — REST + WebSocket (read-only)
          ↓
UNIFIED DASHBOARD
  Next.js + Mapbox + D3.js
  Global Flow Map · Rail Comparison Panel · Corridor Deep Dive
  Liquidity Heatmap · FX Signals · Live Signal Feed

The Unified Rail Graph (Neo4j)

The key architectural insight: all four rail categories share one graph.

Every rail — regardless of whether it's SWIFT, Wise, M-Pesa, or Solana — is a node. Every observable flow relationship between rails is an edge. This allows the intelligence layer to ask questions no siloed system can:

"On the Kenya → Germany corridor, how is volume distributed across SWIFT, Wise, M-Pesa, and USDC/Solana — and how is that distribution shifting?"

Graph structure:

- Nodes (examples): swift, sepa_instant, wise, western_union, mpesa_ke, mtn_momo_gh, wave_sn, usdc_solana, usdt_tron, stellar_xlm
- Edges carry: observed_volume_index, fee_index, congestion_score, trend, last_observed

Edge weights update continuously from the streaming layer.

Observer Plugin Architecture

Every rail is connected via a read-only observer plugin. Observers are strictly prohibited from initiating transactions.

class MyRailObserver:
    RAIL_ID       = "My-Rail"
    RAIL_CATEGORY = "remittance"  # banking | remittance | mobile_money | crypto | fx

    def rail_metadata(self) -> dict:
        """Rail registration data for the unified graph."""

    def observe(self) -> dict:
        """
        READ ONLY — pulls current observable metrics.
        Returns: volume_index, fee_index, congestion_score,
                 liquidity_score, active_corridors, signal
        """

Plugin tree:
plugins/
  banking/     swift, sepa, ach, cips
  remittance/  wise, western_union, remitly, worldremit
  mobile_money/ mpesa, mtn_momo, wave, gcash
  crypto/      solana, tron, stellar, bitcoin
  fx/          collector.py

API Endpoints (All Read-Only)

| Category | Method | Endpoint | Description |
|---|---|---|---|
| Corridor | GET | /v1/corridors/{src}-{dst}/intelligence | Full corridor picture |
| Corridor | GET | /v1/corridors/{src}-{dst}/rails/compare | Side-by-side rail comparison |
| Rail | GET | /v1/rails/{rail}/intelligence | Live intelligence for any rail |
| Rail | GET | /v1/rails/surging | Surging rails — all categories |
| Rail | GET | /v1/rails/congested | Congested rails — all categories |
| Rail | GET | /v1/rails/category/{cat} | All rails in a category |
| Rail | GET | /v1/rails/{rail}/history | Historical flow data |
| Rail | GET | /v1/rails/graph | Full unified graph (JSON) |
| Heatmap | GET | /v1/heatmap/snapshot | Global liquidity heatmap |
| FX | GET | /v1/fx/{pair}/signal | FX intelligence + cross-rail pressure |
| FX | GET | /v1/fx/rates | Live rates — 170+ pairs |
| Community | POST | /v1/report-observation | Submit community rail observation |
| Streaming | WS | /v1/stream/rails/all | All rails, all categories — live |
| Streaming | WS | /v1/stream/category/{cat} | Stream a single category |

Data Flow: Cross-Rail Comparison Query Example

GET /v1/corridors/KE-DE/rails/compare

→ SWIFT               vol:0.21  fee:0.89  congestion:medium  2-5 days   declining
→ Wise                vol:0.34  fee:0.31  congestion:low     ~2 hours   rising
→ M-Pesa→USDC→SEPA   vol:0.62  fee:0.08  congestion:low     ~10 secs   rising
→ Western Union       vol:0.17  fee:0.72  congestion:low     minutes    declining

Target latency:  GFOS has zero payment liability by architectural design.

Development Setup

git clone https://github.com/your-org/gfos.git && cd gfos
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

docker-compose up -d                          # Postgres, Neo4j, Redis, Kafka
python scripts/seed_rail_graph.py             # Seed unified rail graph
uvicorn backend.api.main:app --reload         # Intelligence API
cd frontend/dashboard && npm install && npm run dev  # Dashboard

That's the complete content of your architecture.md. Let me know if you'd like to do anything with it — discuss the design, expand a section, generate diagrams, or anything else!
