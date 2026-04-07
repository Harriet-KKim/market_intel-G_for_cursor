from __future__ import annotations

import json
import os
from typing import Any

import httpx

from .events import PipelineEvent, normalize_event


def openai_configured() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())


def enrich_event_with_llm(
    *,
    title: str,
    summary: str,
    feed_id: str,
    company_tier: int,
    model: str = "gpt-4o-mini",
) -> PipelineEvent | None:
    """저비용 모델로 이벤트 필드 보강. 실패 시 None."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    system = (
        "You extract structured intel for a Physical AI market pipeline. "
        "Respond with JSON only: keys event_type, claims (array of short strings), "
        "summary_one_line, strategic_importance (low|medium|high), "
        "claim_confidence (low|medium|high). "
        "event_type must be one of: funding, product_launch, partnership, "
        "regulation_safety, benchmark, deployment, hiring_org, supply_chain, "
        "research_paper, patent, simulation, other."
    )
    user = json.dumps(
        {"title": title, "summary": summary, "feed_id": feed_id, "company_tier": company_tier},
        ensure_ascii=False,
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }
    try:
        with httpx.Client(timeout=60.0) as client:
            r = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
        content = data["choices"][0]["message"]["content"]
        parsed: dict[str, Any] = json.loads(content)
        return normalize_event(parsed)
    except Exception:
        return None


def weekly_synthesis_llm(
    *,
    bundle_text: str,
    model: str = "gpt-4o",
) -> dict[str, Any] | None:
    """고비용 주간 압축. JSON: executive_bullets, top_signals, risks, next_priorities."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    system = (
        "You are a strategy analyst for Physical AI (robotics, humanoids, embodied AI). "
        "Given structured notes of ingested items, output JSON with keys: "
        "executive_bullets (array of 3-5 strings), "
        "top_signals (array of {rank, signal, companies, confidence, importance, why}), "
        "risks (array of strings), next_priorities (array of strings). "
        "Use English or Korean consistent with input. Be concise."
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": bundle_text[:120000]},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.35,
    }
    try:
        with httpx.Client(timeout=120.0) as client:
            r = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception:
        return None
