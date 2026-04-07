from __future__ import annotations

from pathlib import Path

from .paths import vault_dir


def wiki_profile(slug: str, display: str) -> str:
    return f"[[companies/{slug}/profile|{display}]]"


def wiki_source(slug: str, src_id: str) -> str:
    return f"[[companies/{slug}/sources/{src_id}|{src_id}]]"


def wiki_theme(theme_slug: str, label: str) -> str:
    return f"[[themes/{theme_slug}|{label}]]"


def wiki_daily(slug: str, ymd: str) -> str:
    return f"[[companies/{slug}/daily/{ymd}|{ymd}]]"


def theme_labels() -> dict[str, str]:
    return {
        "embodied_ai_platforms": "Embodied AI platforms",
        "humanoid_supply_chain": "Humanoid supply chain",
        "simulation_digital_twin": "Simulation & digital twin",
    }


def write_source_card(
    *,
    company_slug: str,
    display_name: str,
    src_id: str,
    date_ymd: str,
    url: str,
    title: str,
    summary: str,
    feed_id: str,
    source_reliability: str,
    source_type: str,
    needs_verification: bool,
    themes: list[str],
) -> Path:
    vault = vault_dir()
    rel_dir = vault / "companies" / company_slug / "sources"
    rel_dir.mkdir(parents=True, exist_ok=True)
    path = rel_dir / f"{src_id}.md"
    labels = theme_labels()
    theme_links = ", ".join(
        wiki_theme(t, labels.get(t, t.replace("_", " ").title())) for t in themes
    ) or "(none)"

    nv = "Yes" if needs_verification else "No"
    body = f"""---
type: source_card
source_id: {src_id}
company_slug: {company_slug}
date_captured: {date_ymd}
feed_id: {feed_id}
tags:
  - physical-ai/source
---

# Source: {src_id}

- Source ID: `{src_id}`
- Date captured: {date_ymd}
- Company: {wiki_profile(company_slug, display_name)}
- URL: {url}
- Source type: {source_type}
- Language: (detect TBD)

## Raw Summary

- {summary or title}

## Extracted Claims

1. (See pipeline event block / optional LLM)

## Reliability Assessment

- Source reliability: {source_reliability}
- Is this a primary source?: (TBD)
- Is it likely re-reporting another source?: (TBD)
- Caveats: Auto-ingested from RSS.

## Relevance

- Related company: {wiki_profile(company_slug, display_name)}
- Related technology:
- Related event type:
- Themes: {theme_links}

## Usage Decision

- Use in daily log: Yes
- Needs verification: {nv}
- Can affect weekly report: Yes

## Notes

- Linked daily: {wiki_daily(company_slug, date_ymd)}
"""
    path.write_text(body.strip() + "\n", encoding="utf-8")
    return path.relative_to(vault)


def ensure_daily_header(
    path: Path,
    *,
    company_slug: str,
    display_name: str,
    date_ymd: str,
) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"""---
date: {date_ymd}
company_slug: {company_slug}
type: daily_intel
tags:
  - physical-ai/daily
---

# Daily Intel Log

- Date: `{date_ymd}`
- Company: {wiki_profile(company_slug, display_name)}
- Analyst / System: market-intel-pipeline

## Events

### Pipeline-collected

"""
    path.write_text(header, encoding="utf-8")


def append_pipeline_event(
    *,
    company_slug: str,
    display_name: str,
    date_ymd: str,
    src_id: str,
    title: str,
    url: str,
    event_type: str,
    summary: str,
    claim_confidence: str,
    strategic_importance: str,
    themes: list[str],
    feed_id: str,
) -> None:
    vault = vault_dir()
    daily_path = vault / "companies" / company_slug / "daily" / f"{date_ymd}.md"
    ensure_daily_header(
        daily_path,
        company_slug=company_slug,
        display_name=display_name,
        date_ymd=date_ymd,
    )
    labels = theme_labels()
    theme_line = ", ".join(
        wiki_theme(t, labels.get(t, t.replace("_", " ").title())) for t in themes
    )

    block = f"""
#### {src_id}: {title}

- Event type: `{event_type}`
- Related company: {wiki_profile(company_slug, display_name)}
- Summary: {summary}
- Evidence: {wiki_source(company_slug, src_id)} — [{title}]({url})
- Source / feed: `{feed_id}`
- Claim confidence: {claim_confidence}
- Strategic importance: {strategic_importance}
- Themes: {theme_line}

"""
    with daily_path.open(encoding="utf-8", mode="a") as f:
        f.write(block.strip() + "\n\n")
