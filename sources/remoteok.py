"""RemoteOK - keyless remote-jobs API. https://remoteok.com/api

The first element of the response is a legal/metadata notice, not a job.
"""
from __future__ import annotations

from models import Job
from sources import get_json

URL = "https://remoteok.com/api"


def fetch() -> list[Job]:
    data = get_json(URL)
    jobs = []
    for j in data:
        # skip the leading legal notice object
        if not isinstance(j, dict) or "position" not in j:
            continue
        jobs.append(Job(
            source="remoteok",
            external_id=str(j.get("id", "")),
            title=j.get("position", ""),
            company=j.get("company", ""),
            location=j.get("location", "") or "Remote",
            url=j.get("url", ""),
            description=j.get("description", ""),
            remote=True,
            tags=j.get("tags", []) or [],
            posted=j.get("date", ""),
        ))
    return jobs
