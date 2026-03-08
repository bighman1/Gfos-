"""
GFOS API Router — Claude Intelligence Engine
Proxies all Claude API calls server-side.
The API key never touches the browser.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import os
import store

router = APIRouter()

CLAUDE_MODEL  = "claude-sonnet-4-20250514"
SYSTEM_PROMPT = """You are the GFOS Intelligence Engine — the AI analysis layer of the 
Global Financial Operating System. You analyse real-time payment rail data across 
banking, remittance apps, mobile money, and crypto networks simultaneously.

You provide sharp, concise financial intelligence — like a Bloomberg analyst who 
also understands emerging market mobile money and crypto rails.

Rules:
- Keep responses under 200 words
- Use specific numbers from the data provided
- Be direct — no fluff, no disclaimers
- Format with short paragraphs or bullet points
- Always reference at least 2 specific rails by name
- End with one forward-looking signal"""


class AnalysisRequest(BaseModel):
    prompt: str
    context: Optional[dict] = None
    include_live_data: bool = True


class AnalysisResponse(BaseModel):
    analysis: str
    model: str
    data_freshness: Optional[str] = None


@router.post("/analyse", response_model=AnalysisResponse)
async def analyse(request: AnalysisRequest):
    """
    Run Claude AI analysis on GFOS rail data.
    API key stays on the server — never exposed to the browser.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY not configured on server"
        )

    # Optionally enrich context with live store data
    context = request.context or {}
    if request.include_live_data:
        context["live_rails"] = {
            "banking":    list((store.get_sync("rails:banking",    {}) or {}).values())[:4],
            "remittance": list((store.get_sync("rails:remittance", {}) or {}).values())[:3],
            "mobile":     list((store.get_sync("rails:mobile",     {}) or {}).values())[:3],
            "crypto":     list((store.get_sync("rails:crypto",     {}) or {}).values())[:3],
        }
        fx_signals = store.get_sync("fx:signals", {})
        context["live_fx"] = list(fx_signals.values())[:5] if fx_signals else []
        context["last_refresh"] = store.get_sync("last_full_refresh", "unknown")

    import json
    user_message = f"{request.prompt}\n\nLive GFOS Data:\n{json.dumps(context, indent=2)}"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         api_key,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      CLAUDE_MODEL,
                "max_tokens": 1000,
                "system":     SYSTEM_PROMPT,
                "messages":   [{"role": "user", "content": user_message}],
            },
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Claude API error: {resp.status_code}"
        )

    data     = resp.json()
    analysis = data["content"][0]["text"]
    freshness= context.get("last_refresh", "unknown")

    return AnalysisResponse(
        analysis=analysis,
        model=CLAUDE_MODEL,
        data_freshness=freshness,
    )
