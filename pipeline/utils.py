import urllib.parse

_STRIP_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
    "ref", "source", "fbclid", "gclid", "authuser",
    "mc_cid", "mc_eid", "_ga", "igshid",
}


def canonical_url(url: str) -> str:
    """Strip tracking params, normalize to https, remove trailing slash and fragment."""
    p = urllib.parse.urlparse(url)
    netloc = p.netloc.lower()
    path = p.path.rstrip("/") or "/"
    params = [(k, v) for k, v in urllib.parse.parse_qsl(p.query)
              if k.lower() not in _STRIP_PARAMS]
    query = urllib.parse.urlencode(params)
    return urllib.parse.urlunparse(("https", netloc, path, "", query, ""))
