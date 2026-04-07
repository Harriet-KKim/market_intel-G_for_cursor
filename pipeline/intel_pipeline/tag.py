from __future__ import annotations


def match_company_slug_ordered(
    text: str,
    companies_ordered: list[str],
    keywords_by_slug: dict[str, list[str]],
) -> str | None:
    t = text.lower()
    for slug in companies_ordered:
        for kw in keywords_by_slug.get(slug, []):
            if kw in t:
                return slug
    return None
