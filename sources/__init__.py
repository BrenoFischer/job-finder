"""Job sources. Each module exposes fetch() -> list[Job]."""
from __future__ import annotations

import requests

import config

_session = requests.Session()
_session.headers.update({"User-Agent": config.USER_AGENT,
                         "Accept": "application/json"})


def get_json(url, params=None):
    """GET a URL and return parsed JSON, or None on any failure."""
    resp = _session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()
