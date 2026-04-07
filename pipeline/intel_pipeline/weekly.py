from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .config_load import company_display_map
from .llm import weekly_synthesis_llm
from .paths import vault_dir
from .render import wiki_profile
from .state import connect, recent_items_for_weekly


def _iso_week_label(d: datetime) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def _fallback_body(
    week_label: str,
    by_company: dict[str, list[dict]],
    displays: dict[str, str],
) -> str:
    lines = [
        "## 1. Executive Summary",
        "",
        "- (No OpenAI key) Listed below are raw ingested items grouped by company.",
        "",
        "## 2. Top Signals",
        "",
        "| Rank | Signal | Companies | Confidence | Importance | Why it matters |",
        "|------|--------|-----------|------------|------------|----------------|",
    ]
    rank = 0
    for slug, items in sorted(by_company.items(), key=lambda x: (-len(x[1]), x[0])):
        for it in items[:3]:
            rank += 1
            title = (it.get("title") or "")[:80]
            cc = it.get("claim_confidence") or "medium"
            # 테이블 셀 안에는 위키링크 별칭(|)을 쓰지 않음 — 파이프가 테이블을 깨뜨림
            wk = f"[[companies/{slug}/profile]]"
            lines.append(f"| {rank} | {title} | {wk} | {cc} | medium | RSS ingest |")
    if rank == 0:
        lines.append("| — | No items in window | — | — | — | Run `collect` first |")
    lines.extend(["", "## 3. Company Updates", ""])
    for slug, items in sorted(by_company.items()):
        disp = displays.get(slug, slug)
        lines.append(f"### {wiki_profile(slug, disp)}")
        lines.append("")
        for it in items[:15]:
            sid = it.get("src_id") or ""
            t = it.get("title") or ""
            lines.append(f"- {sid}: {t}")
        lines.append("")
    lines.extend(
        [
            "## 4. Theme Updates",
            "",
            "(Link theme notes under [[themes/embodied_ai_platforms]] etc.)",
            "",
            "## 5. Risks and Open Questions",
            "",
            "-",
            "",
            "## 6. Strategic Implications",
            "",
            "-",
            "",
            "## 7. Next-week Research Priorities",
            "",
            "- Review `needs_verification` source cards",
            "",
        ]
    )
    return "\n".join(lines)


def run_weekly(days: int = 7) -> int:
    now = datetime.now(timezone.utc)
    week_label = _iso_week_label(now)
    displays = company_display_map()
    with connect() as conn:
        items = recent_items_for_weekly(conn, days=days)

    by_company: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        slug = str(it.get("company_slug") or "")
        if slug:
            by_company[slug].append(it)

    bundle = {
        "week": week_label,
        "items": [
            {
                "company": it.get("company_slug"),
                "title": it.get("title"),
                "event_type": it.get("event_type"),
                "src_id": it.get("src_id"),
                "claim_confidence": it.get("claim_confidence"),
            }
            for it in items
        ],
    }
    bundle_text = json.dumps(bundle, ensure_ascii=False, indent=2)

    synth = weekly_synthesis_llm(bundle_text=bundle_text)
    vault = vault_dir()
    out_dir = vault / "reports" / "weekly_strategy"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{week_label}.md"

    header = f"""---
week: {week_label}
type: weekly_strategy
tags:
  - physical-ai/weekly
---

# Weekly Strategy Report — Physical AI

- Week: {week_label}
- Scope: Physical AI (pipeline)
- Prepared by: market-intel-pipeline

"""

    if synth and isinstance(synth, dict):
        exec_bullets = synth.get("executive_bullets") or []
        top = synth.get("top_signals") or []
        risks = synth.get("risks") or []
        nxt = synth.get("next_priorities") or []

        body_lines = ["## 1. Executive Summary", ""]
        for b in exec_bullets:
            body_lines.append(f"- {b}")
        body_lines.extend(["", "## 2. Top Signals", "", "| Rank | Signal | Companies | Confidence | Importance | Why it matters |", "|------|--------|-----------|------------|------------|----------------|"])
        for i, row in enumerate(top, start=1):
            if not isinstance(row, dict):
                continue
            def _cell(s: str) -> str:
                return str(s).replace("|", "/").replace("\n", " ")[:240]

            sig = _cell(row.get("signal", ""))
            comps = _cell(row.get("companies", ""))
            conf = _cell(row.get("confidence", ""))
            imp = _cell(row.get("importance", ""))
            why = _cell(row.get("why", ""))
            body_lines.append(f"| {i} | {sig} | {comps} | {conf} | {imp} | {why} |")
        body_lines.extend(["", "## 3. Company Updates", ""])
        for slug, rows in sorted(by_company.items()):
            disp = displays.get(slug, slug)
            body_lines.append(f"### {wiki_profile(slug, disp)}")
            body_lines.append("")
            for it in rows[:20]:
                body_lines.append(f"- [[companies/{slug}/sources/{it.get('src_id')}|{it.get('src_id')}]] — {it.get('title')}")
            body_lines.append("")
        body_lines.extend(["## 5. Risks and Open Questions", ""])
        for r in risks:
            body_lines.append(f"- {r}")
        body_lines.extend(["", "## 7. Next-week Research Priorities", ""])
        for p in nxt:
            body_lines.append(f"- {p}")
        body = "\n".join(body_lines) + "\n"
    else:
        body = _fallback_body(week_label, by_company, displays)

    out_path.write_text(header + body, encoding="utf-8")
    return 0
