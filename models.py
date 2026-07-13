"""Shared data model for a job posting."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field


@dataclass
class Job:
    source: str            # which API it came from, e.g. "remotive"
    external_id: str       # id from the source (used for dedup)
    title: str
    company: str
    location: str          # human-readable location string
    url: str               # link to apply / view
    description: str = ""   # plain-ish text, used for years-of-experience scan
    remote: bool = False    # True if the role is remote
    tags: list[str] = field(default_factory=list)
    posted: str = ""       # ISO date string if available

    def key(self) -> str:
        """Stable id used for deduplication across runs.

        Prefer source + external id; fall back to a hash of the URL so that
        the same posting is never shown twice even if ids are missing.
        """
        base = f"{self.source}:{self.external_id}".strip().lower()
        if not self.external_id:
            base = self.url.strip().lower()
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]

    @property
    def clean_description(self) -> str:
        """Description with HTML tags stripped and whitespace collapsed."""
        text = re.sub(r"<[^>]+>", " ", self.description or "")
        return re.sub(r"\s+", " ", text).strip()
