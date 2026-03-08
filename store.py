"""
GFOS In-Memory Store
Shared data cache — collectors write here, routers read from here.
In production this would be Redis. For now it's a simple dict in memory.
"""

from typing import Dict, Any
import asyncio

_store: Dict[str, Any] = {}
_lock = asyncio.Lock()


async def set(key: str, value: Any):
    async with _lock:
        _store[key] = value


async def get(key: str, default=None) -> Any:
    return _store.get(key, default)


async def get_all() -> Dict[str, Any]:
    return dict(_store)


def get_sync(key: str, default=None) -> Any:
    """Synchronous get — use only outside async context."""
    return _store.get(key, default)


def set_sync(key: str, value: Any):
    """Synchronous set — use only during startup seeding."""
    _store[key] = value
