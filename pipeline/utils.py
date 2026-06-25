import re
import urllib.parse

_STRIP_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
    "ref", "source", "fbclid", "gclid", "authuser",
    "mc_cid", "mc_eid", "_ga", "igshid",
    "hl",
}


def sanitize_title(title: str) -> str:
    """Collapse whitespace (including newlines) into single spaces and strip."""
    return re.sub(r'\s+', ' ', title).strip()


def extract_balanced_json(text: str, open_ch: str, close_ch: str) -> str | None:
    """Find the first open_ch and return the substring up to its balanced close_ch.

    String-aware: brackets inside JSON string literals (e.g. a title containing
    "[Tested]") don't affect the depth count. Returns None if no balanced match.
    """
    start = text.find(open_ch)
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(text[start:], start):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def canonical_url(url: str) -> str:
    """Strip tracking params, normalize to https, remove trailing slash and fragment."""
    p = urllib.parse.urlparse(url)
    netloc = p.netloc.lower()
    path = p.path.rstrip("/") or "/"
    params = [(k, v) for k, v in urllib.parse.parse_qsl(p.query)
              if k.lower() not in _STRIP_PARAMS]
    query = urllib.parse.urlencode(params)
    return urllib.parse.urlunparse(("https", netloc, path, "", query, ""))
