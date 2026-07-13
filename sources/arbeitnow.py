"""Arbeitnow - keyless, Europe-focused job board.
https://www.arbeitnow.com/api/job-board-api
"""
from __future__ import annotations

from models import Job
from sources import get_json

URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch() -> list[Job]:
    data = get_json(URL)
    jobs = []
    for j in data.get("data", []):
        slug = j.get("slug", "")
        jobs.append(Job(
            source="arbeitnow",
            external_id=slug,
            title=j.get("title", ""),
            company=j.get("company_name", ""),
            location=j.get("location", "") or "Europe",
            url=j.get("url") or f"https://www.arbeitnow.com/view/{slug}",
            description=j.get("description", ""),
            remote=bool(j.get("remote", False)),
            tags=(j.get("tags", []) or []) + (j.get("job_types", []) or []),
            posted=str(j.get("created_at", "")),
        ))
    return jobs
