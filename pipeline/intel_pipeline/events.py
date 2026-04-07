from __future__ import annotations

from typing import Any, TypedDict


class PipelineEvent(TypedDict, total=False):
    """Event Builder 출력(JSON 직렬화 가능)."""

    event_type: str
    claims: list[str]
    summary_one_line: str
    strategic_importance: str
    claim_confidence: str


VALID_EVENT_TYPES = frozenset(
    {
        "funding",
        "product_launch",
        "partnership",
        "regulation_safety",
        "benchmark",
        "deployment",
        "hiring_org",
        "supply_chain",
        "research_paper",
        "patent",
        "simulation",
        "other",
    }
)


def normalize_event(raw: dict[str, Any]) -> PipelineEvent:
    et = str(raw.get("event_type") or "other")
    if et not in VALID_EVENT_TYPES:
        et = "other"
    claims = raw.get("claims")
    if not isinstance(claims, list):
        claims = []
    claims = [str(c).strip() for c in claims if str(c).strip()][:5]
    summary = str(raw.get("summary_one_line") or "").strip() or str(raw.get("summary") or "")
    imp = str(raw.get("strategic_importance") or "medium").lower()
    if imp not in ("low", "medium", "high"):
        imp = "medium"
    cc = str(raw.get("claim_confidence") or "medium").lower()
    if cc not in ("low", "medium", "high"):
        cc = "medium"
    return PipelineEvent(
        event_type=et,
        claims=claims,
        summary_one_line=summary,
        strategic_importance=imp,
        claim_confidence=cc,
    )


def heuristic_event(
    *,
    title: str,
    summary: str,
    feed_id: str,
    company_tier: int,
) -> PipelineEvent:
    text = (title + " " + (summary or "")).lower()
    if feed_id == "arxiv_cs_ro" or "arxiv" in text:
        et = "research_paper"
    elif any(x in text for x in ("funding", "raises", "million", "series ")):
        et = "funding"
    elif any(x in text for x in ("partnership", "partners with", "collaborat")):
        et = "partnership"
    elif any(x in text for x in ("launch", "announces", "unveil")):
        et = "product_launch"
    else:
        et = "other"
    imp = "high" if company_tier <= 1 else "medium"
    return normalize_event(
        {
            "event_type": et,
            "claims": [title[:200]],
            "summary_one_line": (summary or title)[:500],
            "strategic_importance": imp,
            "claim_confidence": "low" if feed_id == "techcrunch_robotics" else "medium",
        }
    )
