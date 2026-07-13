"""The Muse - keyless public jobs API (higher limits with a free key).
https://www.themuse.com/api/public/jobs
"""
from __future__ import annotations

from models import Job
from sources import get_json

URL = "https://www.themuse.com/api/public/jobs"


def fetch() -> list[Job]:
    jobs = []
    seen = set()
    for category in ("Software Engineering",):
        for page in (0, 1, 2):
            try:
                data = get_json(URL, params={
                    "category": category, "page": page, "descending": "true",
                })
            except Exception:
                continue
            for j in data.get("results", []):
                jid = str(j.get("id", ""))
                if jid in seen:
                    continue
                seen.add(jid)
                locations = ", ".join(
                    l.get("name", "") for l in j.get("locations", []))
                remote = "remote" in locations.lower() or \
                    "flexible" in locations.lower()
                levels = [l.get("name", "") for l in j.get("levels", [])]
                level_text = " ".join(levels).lower()
                # The Muse tags seniority explicitly; drop clearly senior roles.
                if level_text and all(
                    lv in level_text for lv in ["senior"]) and \
                        "entry" not in level_text and "mid" not in level_text:
                    continue
                if "management" in level_text and "mid" not in level_text \
                        and "entry" not in level_text:
                    continue
                jobs.append(Job(
                    source="themuse",
                    external_id=jid,
                    title=j.get("name", ""),
                    company=(j.get("company") or {}).get("name", ""),
                    location=locations or "Unknown",
                    url=(j.get("refs") or {}).get("landing_page", ""),
                    description=j.get("contents", ""),
                    remote=remote,
                    tags=levels,
                    posted=j.get("publication_date", ""),
                ))
    return jobs
