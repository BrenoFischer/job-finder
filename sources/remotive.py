"""Remotive - keyless remote-jobs API. https://remotive.com/api/remote-jobs"""
from __future__ import annotations

from models import Job
from sources import get_json

URL = "https://remotive.com/api/remote-jobs"


def fetch() -> list[Job]:
    data = get_json(URL, params={"category": "software-dev", "limit": 100})
    jobs = []
    for j in data.get("jobs", []):
        jobs.append(Job(
            source="remotive",
            external_id=str(j.get("id", "")),
            title=j.get("title", ""),
            company=j.get("company_name", ""),
            location=j.get("candidate_required_location", "") or "Remote",
            url=j.get("url", ""),
            description=j.get("description", ""),
            remote=True,
            tags=j.get("tags", []) or [],
            posted=j.get("publication_date", ""),
        ))
    return jobs
