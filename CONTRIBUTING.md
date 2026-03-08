# Contributing to GFOS

Welcome — and thank you for wanting to help build the intelligence layer the global payments market has never had.

GFOS is built in public. Every architectural decision, every data model, every debate happens here in the open. We believe intelligence about how money flows globally should be a community commons, not a proprietary black box locked inside a Bloomberg terminal.

---

## What GFOS Builds (and Doesn't)

Before contributing, one principle to internalise:

**GFOS observes payment rails. It does not operate them.**

This means:
- ✅ We build observers that read rail status, volume indicators, and fee signals
- ✅ We build intelligence engines that detect patterns, congestion, and liquidity shifts
- ✅ We build APIs that surface that intelligence to the world
- ❌ We do not build anything that initiates, authorises, or routes payments
- ❌ We do not build anything that touches user funds

Every contribution should pass that test.

---

## Where to Start

Look for issues tagged [`good first issue`](../../issues?q=label%3A%22good+first+issue%22). These are scoped, well-documented tasks that don't require deep system knowledge.

**High-Impact Areas Right Now (Phase 1–2)**
- Rail observer plugins — connect new rails as read-only observers
- Data collectors — FX APIs, blockchain volume feeds, mobile money status APIs
- Intelligence engine — flow analysis, congestion detection algorithms
- Tests — coverage is a priority from day one

---

## Adding a Rail Observer Plugin

This is the fastest way to contribute meaningfully. Each plugin connects a new payment rail as a read-only observer, expanding GFOS's intelligence coverage.

### 1. Create your plugin folder

```
plugins/
  your_rail/
    observer.py       ← required
    README.md         ← required
    tests/
      test_observer.py
```

### 2. Implement the observer interface

```python
class YourRailObserver:
    """
    Read-only observer for [Rail Name].

    This observer pulls publicly available or API-accessible metrics
    from the rail. It NEVER initiates transactions.
    """

    RAIL_ID   = "YourRail"       # e.g. "MTN-MoMo", "Orange-Money"
    RAIL_TYPE = "mobile_money"   # banking | mobile_money | crypto | card | fx
    CURRENCY  = "GHS"

    def rail_metadata(self) -> dict:
        """Rail registration data for the GFOS graph."""
        return {
            "rail_id":   self.RAIL_ID,
            "rail_type": self.RAIL_TYPE,
            "currency":  self.CURRENCY,
            "countries": ["GH"],   # ISO 3166-1 alpha-2
        }

    def observe(self) -> dict:
        """
        Pull current observable metrics from this rail.
        Called on a schedule by the GFOS data collector.

        READ ONLY — may only call status/query APIs.
        Must never initiate a transaction.

        Returns:
            dict with volume_index, fee_index, congestion_score, liquidity_score
        """
        # Query the rail's status API, developer portal, or public feed
        # Return normalised metrics for the intelligence engine
        return {
            "rail":             self.RAIL_ID,
            "volume_index":     0.61,    # 0–1, relative to rail's own baseline
            "fee_index":        0.34,    # 0–1, relative to rail's own baseline
            "congestion_score": 0.12,    # 0–1 (higher = more congested)
            "liquidity_score":  0.78,    # 0–1 (higher = deeper liquidity)
            "signal":           "stable",
            "active_corridors": ["GH-NG", "GH-SN"],
        }
```

### 3. Write tests

Tests must use mocked/sandbox responses — never call production APIs in tests.

```python
# tests/test_observer.py
from unittest.mock import patch
from plugins.your_rail.observer import YourRailObserver

def test_observe_returns_valid_metrics():
    observer = YourRailObserver()
    with patch.object(observer, '_fetch_status', return_value=mock_response()):
        result = observer.observe()
        assert 0 <= result["volume_index"] <= 1
        assert 0 <= result["congestion_score"] <= 1
        assert "active_corridors" in result
```

### 4. Open a PR

Title format: `feat(plugin): add MTN MoMo observer`

---

## Contribution Types

| Type | Examples |
|------|---------|
| **Rail observers** | MTN MoMo, Orange Money, Wave, GCash, WeChat Pay, Pix (Brazil) |
| **Data collectors** | FX sources, blockchain volume feeds, central bank data |
| **Intelligence engine** | Flow analysis algorithms, congestion detection, pattern models |
| **AI / ML** | Time-series forecasting, seasonal pattern detection |
| **Heatmap** | Liquidity modelling, visualisation data structures |
| **Frontend** | Dashboard panels, Mapbox visualisation, rail performance charts |
| **Regulation Pulse** | Country restriction tracking, FATF update collectors |
| **Docs** | Architecture guides, corridor analysis, API docs |

---

## Development Setup

```bash
git clone https://github.com/your-org/gfos.git
cd gfos

# Python environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Infrastructure (Postgres, Neo4j, Redis, Kafka)
docker-compose up -d

# Run intelligence API
uvicorn backend.api.main:app --reload

# Run tests
pytest
```

---

## Code Standards

- **Python 3.11+**, type hints everywhere
- **Black** for formatting (`black .`)
- **Ruff** for linting (`ruff check .`)
- **Pytest** for tests — aim for >80% coverage on new code
- **Conventional Commits** — `feat:`, `fix:`, `docs:`, `refactor:`

---

## Pull Request Process

1. Fork and branch: `git checkout -b feat/mtn-momo-observer`
2. Build with tests
3. `black . && ruff check . && pytest`
4. Open a PR with a clear description of what the observer connects and what data it surfaces
5. A maintainer will review within 48–72 hours

---

## Community

- **Discussions** — [GitHub Discussions](../../discussions) — architecture, ideas, questions
- **Issues** — [GitHub Issues](../../issues) — bugs and feature requests

We are building something the global financial system genuinely lacks. Glad you are here.
