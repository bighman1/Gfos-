"""
GFOS Background Scheduler
Runs all data collectors on a schedule.

Schedule:
  - Crypto rails    : every 5 minutes  (CoinGecko free tier is generous)
  - FX rates        : every 60 minutes (free tier limit aware)
  - Banking/Mobile  : every 10 minutes (synthetic — no rate limit)
"""

import asyncio
from datetime import datetime, timezone

from collectors import crypto, fx, rails
import store


async def run_all_collectors():
    """Run all collectors once — called on startup and by scheduler."""
    await asyncio.gather(
        crypto.collect(),
        fx.collect(),
        rails.collect(),
        return_exceptions=True,
    )
    await store.set("last_full_refresh", datetime.now(timezone.utc).isoformat())
    print("[Scheduler] All collectors complete ✓")


_tasks = []


async def start_scheduler():
    """Start background collection tasks."""
    print("[Scheduler] Starting GFOS data collectors...")

    # Run once immediately on startup
    await run_all_collectors()

    # Then schedule on timers
    async def crypto_loop():
        while True:
            await asyncio.sleep(300)  # 5 minutes
            try:
                await crypto.collect()
            except Exception as e:
                print(f"[Scheduler] Crypto collector error: {e}")

    async def fx_loop():
        while True:
            await asyncio.sleep(3600)  # 60 minutes
            try:
                await fx.collect()
            except Exception as e:
                print(f"[Scheduler] FX collector error: {e}")

    async def rails_loop():
        while True:
            await asyncio.sleep(600)  # 10 minutes
            try:
                await rails.collect()
            except Exception as e:
                print(f"[Scheduler] Rail collector error: {e}")

    _tasks.append(asyncio.create_task(crypto_loop()))
    _tasks.append(asyncio.create_task(fx_loop()))
    _tasks.append(asyncio.create_task(rails_loop()))

    print("[Scheduler] Background collectors running ✓")


async def stop_scheduler():
    """Cancel all background tasks on shutdown."""
    for task in _tasks:
        task.cancel()
    print("[Scheduler] Collectors stopped.")
