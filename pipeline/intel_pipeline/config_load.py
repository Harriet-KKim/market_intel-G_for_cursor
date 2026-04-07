from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .paths import config_dir


def _load_yaml(name: str) -> dict[str, Any]:
    path = config_dir() / name
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def load_companies() -> list[dict[str, Any]]:
    raw = _load_yaml("companies.yaml")
    companies = raw.get("companies")
    return list(companies) if isinstance(companies, list) else []


def company_display_map() -> dict[str, str]:
    out: dict[str, str] = {}
    for c in load_companies():
        slug = c.get("slug")
        name = c.get("display_name")
        if isinstance(slug, str) and isinstance(name, str):
            out[slug] = name
    return out


def company_themes_map() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for c in load_companies():
        slug = c.get("slug")
        themes = c.get("themes")
        if isinstance(slug, str) and isinstance(themes, list):
            out[slug] = [str(t) for t in themes]
    return out


def load_keywords() -> dict[str, list[str]]:
    raw = _load_yaml("keywords.yaml")
    out: dict[str, list[str]] = {}
    for k, v in raw.items():
        if isinstance(k, str) and isinstance(v, list):
            out[k] = [str(x).lower() for x in v]
    return out


def load_sources() -> dict[str, Any]:
    return _load_yaml("sources.yaml")
