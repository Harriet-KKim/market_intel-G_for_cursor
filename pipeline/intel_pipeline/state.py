from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Generator

from .paths import state_db_path


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@contextmanager
def connect() -> Generator[sqlite3.Connection, None, None]:
    path = state_db_path()
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        init_schema(conn)
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS feed_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_canonical TEXT NOT NULL UNIQUE,
            feed_id TEXT,
            title TEXT,
            summary TEXT,
            link_original TEXT,
            published TEXT,
            company_slug TEXT NOT NULL,
            src_id TEXT NOT NULL,
            source_card_rel TEXT,
            event_type TEXT,
            claim_confidence TEXT,
            needs_verification INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_feed_items_company ON feed_items(company_slug);
        CREATE INDEX IF NOT EXISTS idx_feed_items_created ON feed_items(created_at);

        CREATE TABLE IF NOT EXISTS kpi_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at TEXT NOT NULL,
            feeds_fetched INTEGER,
            new_items INTEGER,
            skipped_dup INTEGER,
            skipped_no_company INTEGER,
            errors INTEGER
        );
        """
    )


def url_exists(conn: sqlite3.Connection, url_canonical: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM feed_items WHERE url_canonical = ? LIMIT 1",
        (url_canonical,),
    )
    return cur.fetchone() is not None


def next_src_id(conn: sqlite3.Connection, day_yyyymmdd: str) -> str:
    like = f"SRC-{day_yyyymmdd}-%"
    cur = conn.execute(
        "SELECT src_id FROM feed_items WHERE src_id LIKE ? ORDER BY src_id DESC LIMIT 1",
        (like,),
    )
    row = cur.fetchone()
    n = 0
    if row and row[0]:
        parts = str(row[0]).rsplit("-", 1)
        if len(parts) == 2 and parts[1].isdigit():
            n = int(parts[1])
    return f"SRC-{day_yyyymmdd}-{n + 1:03d}"


def insert_item(
    conn: sqlite3.Connection,
    *,
    url_canonical: str,
    feed_id: str,
    title: str,
    summary: str,
    link_original: str,
    published: str | None,
    company_slug: str,
    src_id: str,
    source_card_rel: str,
    event_type: str,
    claim_confidence: str,
    needs_verification: bool,
) -> None:
    conn.execute(
        """
        INSERT INTO feed_items (
            url_canonical, feed_id, title, summary, link_original, published,
            company_slug, src_id, source_card_rel, event_type, claim_confidence,
            needs_verification, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            url_canonical,
            feed_id,
            title,
            summary,
            link_original,
            published or "",
            company_slug,
            src_id,
            source_card_rel,
            event_type,
            claim_confidence,
            1 if needs_verification else 0,
            _utc_now_iso(),
        ),
    )


def log_kpi(
    conn: sqlite3.Connection,
    *,
    feeds_fetched: int,
    new_items: int,
    skipped_dup: int,
    skipped_no_company: int,
    errors: int,
) -> None:
    conn.execute(
        """
        INSERT INTO kpi_runs (run_at, feeds_fetched, new_items, skipped_dup, skipped_no_company, errors)
        VALUES (?,?,?,?,?,?)
        """,
        (
            _utc_now_iso(),
            feeds_fetched,
            new_items,
            skipped_dup,
            skipped_no_company,
            errors,
        ),
    )


def _parse_created(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def recent_items_for_weekly(conn: sqlite3.Connection, days: int = 7) -> list[dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=int(days))
    cur = conn.execute("SELECT * FROM feed_items ORDER BY id DESC")
    out: list[dict[str, Any]] = []
    for r in cur.fetchall():
        row = dict(r)
        t = _parse_created(row.get("created_at"))
        if t is not None and t >= cutoff:
            out.append(row)
    return out
