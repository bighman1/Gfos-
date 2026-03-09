from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import os
import json
import store

router = APIRouter()

class AnalysisRequest(BaseModel):
    prompt: str
    context: Optional[dict] = None
    include_live_data: bool = True

@router.post("/analyse")
async def analyse(request: AnalysisRequest):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not configured")

    context = request.context or {}
    if request.include_live_data:
        context["live_rails"] = {
            "banking":    list((store.get_sync("rails:banking",    {}) or {}).values())[:4],
            "remittance": list((store.get_sync("rails:remittance", {}) or {}).values())[:3],
            "mobile":     list((store.get_sync("rails:mobile",     {}) or {}).values())[:3],
            "crypto":     list((store.get_sync("rails:crypto",     {}) or {}).values())[:3],
        }
        context["last_refresh"] = store.get_sync("last_full_refresh", "unknown")

    user_message = f"{request.prompt}\n\nLive GFOS Data:\n{json.dumps(context, indent=2)}"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "system": "You are the GFOS Intelligence Engine. Analyse payment rail data across banking, remittance, mobile money and crypto. Be concise, direct, use specific numbers. Under 200 words.",
                "messages": [{"role": "user", "content": user_message}],
            },
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Claude API error: {resp.status_code}")

    data = resp.json()
    return {
        "analysis": data["content"][0]["text"],
        "model": "claude-sonnet-4-20250514",
        "data_freshness": context.get("last_refresh", "unknown"),
        }
