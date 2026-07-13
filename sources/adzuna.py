"""Adzuna - Ireland job search (needs a free app_id + app_key).
https://developer.adzuna.com/

Set ADZUNA_APP_ID and ADZUNA_APP_KEY in the environment. If they are missing
this source quietly returns nothing, so the tool still works without it.
"""
from __future__ import annotations

import os

from models import Job
from sources import get_json

BASE = "https://api.adzuna.com/v1/api/jobs/ie/search/1"

# Keyword groups run as separate searches (Adzuna's "what" is a phrase).
QUERIES = [
    "frontend developer",
    "react developer",
    "software developer",
    "javascript developer",
]


def fetch() -> list[Job]:
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        return []

    jobs = []
    seen = set()
    for what in QUERIES:
        try:
            data = get_json(BASE, params={
                "app_id": app_id,
                "app_key": app_key,
                "results_per_page": 50,
                "what": what,
                "max_days_old": 3,
                "content-type": "application/json",
            })
        except Exception:
            continue
        for j in data.get("results", []):
            jid = str(j.get("id", ""))
            if jid in seen:
                continue
            seen.add(jid)
            loc = (j.get("location") or {}).get("display_name", "") or "Ireland"
            desc = j.get("description", "")
            contract = (j.get("contract_time") or "")
            remote = "remote" in (loc + " " + desc).lower() or \
                "hybrid" in (loc + " " + desc).lower()
            jobs.append(Job(
                source="adzuna",
                external_id=jid,
                title=j.get("title", ""),
                company=(j.get("company") or {}).get("display_name", ""),
                location=loc,
                url=j.get("redirect_url", ""),
                description=desc,
                remote=remote,
                tags=[contract] if contract else [],
                posted=str(j.get("created", "")),
            ))
    return jobs
