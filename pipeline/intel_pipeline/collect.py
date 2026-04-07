from __future__ import annotations

import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import feedparser
import httpx

from .config_load import (
    company_display_map,
    company_themes_map,
    load_companies,
    load_keywords,
    load_sources,
)
from .dedup import canonicalize_url
from .events import heuristic_event
from .llm import enrich_event_with_llm
from .paths import kpi_log_path
from .render import append_pipeline_event, write_source_card
from .state import connect, log_kpi, next_src_id, url_exists, insert_item
from .tag import match_company_slug_ordered


def _entry_published(entry: Any) -> str | None:
    for key in ("published", "updated"):
        raw = getattr(entry, key, None)
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
            except (TypeError, ValueError, OverflowError):
                pass
    return None


def _entry_link(entry: Any) -> str:
    link = getattr(entry, "link", None) or ""
    if not link and getattr(entry, "links", None):
        for l in entry.links:
            if l.get("rel") == "alternate" and l.get("href"):
                return str(l["href"])
    return str(link)


def _entry_summary(entry: Any) -> str:
    if getattr(entry, "summary", None):
        return str(entry.summary)
    if getattr(entry, "description", None):
        return str(entry.description)
    return ""


def _company_tier(companies: list[dict[str, Any]], slug: str) -> int:
    for c in companies:
        if c.get("slug") == slug:
            t = c.get("tier")
            return int(t) if isinstance(t, int) else 99
    return 99


def run_collect() -> int:
    sources_cfg = load_sources()
    companies = load_companies()
    companies.sort(key=lambda c: (int(c.get("tier", 99)), str(c.get("slug", ""))))
    ordered_slugs = [str(c["slug"]) for c in companies if c.get("slug")]
    keywords = load_keywords()
    displays = company_display_map()
    themes_map = company_themes_map()

    defaults = sources_cfg.get("defaults") or {}
    timeout = float(defaults.get("request_timeout_seconds", 25))
    ua = str(defaults.get("user_agent", "MarketIntel/1.0"))

    feeds = sources_cfg.get("feeds") or []
    feeds_fetched = 0
    new_items = 0
    skipped_dup = 0
    skipped_no_company = 0
    errors = 0

    day_utc = datetime.now(timezone.utc).strftime("%Y%m%d")
    date_ymd = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    with connect() as conn:
        for feed in feeds:
            if not isinstance(feed, dict):
                continue
            fid = str(feed.get("id", ""))
            url = str(feed.get("url", ""))
            if not url:
                continue
            feeds_fetched += 1
            try:
                with httpx.Client(
                    timeout=timeout,
                    headers={"User-Agent": ua},
                    follow_redirects=True,
                ) as client:
                    r = client.get(url)
                    r.raise_for_status()
                parsed = feedparser.parse(r.content)
            except Exception:
                errors += 1
                continue

            rel = float(feed.get("source_reliability", defaults.get("source_reliability", 0.5)))
            stype = str(feed.get("source_type", "rss"))
            themes_hint = feed.get("themes_hint") or []
            hint_list = [str(t) for t in themes_hint] if isinstance(themes_hint, list) else []

            for entry in getattr(parsed, "entries", []) or []:
                link = _entry_link(entry)
                if not link:
                    continue
                canon = canonicalize_url(link)
                if url_exists(conn, canon):
                    skipped_dup += 1
                    continue

                title = str(getattr(entry, "title", "") or "(no title)")
                summary = _entry_summary(entry)
                blob = title + " " + summary
                slug = match_company_slug_ordered(blob, ordered_slugs, keywords)
                if not slug:
                    skipped_no_company += 1
                    continue

                src_id = next_src_id(conn, day_utc)
                display = displays.get(slug, slug)
                tier = _company_tier(companies, slug)

                ev = enrich_event_with_llm(
                    title=title,
                    summary=summary,
                    feed_id=fid,
                    company_tier=tier,
                )
                if ev is None:
                    ev = heuristic_event(
                        title=title,
                        summary=summary,
                        feed_id=fid,
                        company_tier=tier,
                    )

                themes = list(dict.fromkeys(themes_map.get(slug, []) + hint_list))
                needs_verification = rel < 0.65 or fid == "techcrunch_robotics"

                card_rel = write_source_card(
                    company_slug=slug,
                    display_name=display,
                    src_id=src_id,
                    date_ymd=date_ymd,
                    url=link,
                    title=title,
                    summary=ev.get("summary_one_line") or summary,
                    feed_id=fid,
                    source_reliability=str(rel),
                    source_type=stype,
                    needs_verification=needs_verification,
                    themes=themes,
                )

                append_pipeline_event(
                    company_slug=slug,
                    display_name=display,
                    date_ymd=date_ymd,
                    src_id=src_id,
                    title=title,
                    url=link,
                    event_type=str(ev.get("event_type", "other")),
                    summary=str(ev.get("summary_one_line") or summary)[:800],
                    claim_confidence=str(ev.get("claim_confidence", "medium")),
                    strategic_importance=str(ev.get("strategic_importance", "medium")),
                    themes=themes,
                    feed_id=fid,
                )

                insert_item(
                    conn,
                    url_canonical=canon,
                    feed_id=fid,
                    title=title,
                    summary=summary[:4000],
                    link_original=link,
                    published=_entry_published(entry),
                    company_slug=slug,
                    src_id=src_id,
                    source_card_rel=str(card_rel).replace("\\", "/"),
                    event_type=str(ev.get("event_type", "other")),
                    claim_confidence=str(ev.get("claim_confidence", "medium")),
                    needs_verification=needs_verification,
                )
                new_items += 1

        log_kpi(
            conn,
            feeds_fetched=feeds_fetched,
            new_items=new_items,
            skipped_dup=skipped_dup,
            skipped_no_company=skipped_no_company,
            errors=errors,
        )

    kpi_line = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "feeds_fetched": feeds_fetched,
        "new_items": new_items,
        "skipped_dup": skipped_dup,
        "skipped_no_company": skipped_no_company,
        "errors": errors,
    }
    with kpi_log_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(kpi_line, ensure_ascii=False) + "\n")

    return 0
