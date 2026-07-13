"""Jobicy - keyless remote-jobs API with geo + level fields.
https://jobicy.com/api/v2/remote-jobs
"""
from __future__ import annotations

from models import Job
from sources import get_json

URL = "https://jobicy.com/api/v2/remote-jobs"


def fetch() -> list[Job]:
    jobs = []
    seen = set()
    # Query the geographies we care about; "anywhere" catches global roles.
    for geo in ("europe", "usa", "anywhere"):
        try:
            data = get_json(URL, params={"count": 50, "geo": geo,
                                         "industry": "dev"})
        except Exception:
            continue
        for j in data.get("jobs", []):
            jid = str(j.get("id", ""))
            if jid in seen:
                continue
            seen.add(jid)
            jobs.append(Job(
                source="jobicy",
                external_id=jid,
                title=j.get("jobTitle", ""),
                company=j.get("companyName", ""),
                location=j.get("jobGeo", "") or "Remote",
                url=j.get("url", ""),
                description=j.get("jobExcerpt", "") or j.get("jobDescription", ""),
                remote=True,
                tags=[j.get("jobLevel", "")] if j.get("jobLevel") else [],
                posted=j.get("pubDate", ""),
            ))
    return jobs
