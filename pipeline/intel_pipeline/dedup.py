from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def canonicalize_url(url: str) -> str:
    """쿼리 정렬·프래그먼트 제거 등 가벼운 정규화."""
    try:
        p = urlparse(url.strip())
    except Exception:
        return url.strip().lower()
    scheme = (p.scheme or "http").lower()
    netloc = (p.netloc or "").lower()
    path = p.path or "/"
    q = parse_qsl(p.query, keep_blank_values=True)
    q.sort()
    query = urlencode(q)
    return urlunparse((scheme, netloc, path, "", query, ""))
