"""Decide whether a Job matches Breno's search criteria."""
from __future__ import annotations

import re

import config
from models import Job


def _title_included(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in config.INCLUDE_TITLE)


def _title_excluded(title: str) -> bool:
    t = title.lower()
    for word in config.EXCLUDE_TITLE_WORDS:
        # whole-word match so "lead" doesn't hit "leadership tools" etc.
        if re.search(rf"\b{re.escape(word)}\b", t):
            return True
    return False


def _demands_too_much_experience(description: str) -> bool:
    """True if the text requires >= MAX_YEARS_EXPERIENCE years.

    Handles "5+ years", "at least 6 years", "minimum 5 years of",
    and ranges like "5-7 years" (uses the lower bound).
    """
    text = description.lower()
    for match in re.finditer(
        r"(\d{1,2})\s*(?:\+|to|-|–|—)?\s*(?:\d{1,2})?\s*years?", text
    ):
        try:
            lower_bound = int(match.group(1))
        except (TypeError, ValueError):
            continue
        if 0 < lower_bound < 30 and lower_bound >= config.MAX_YEARS_EXPERIENCE:
            return True
    return False


def _has(term_list, text: str) -> bool:
    """Whole-word / phrase match, so 'us' won't hit 'business' etc."""
    return any(
        re.search(rf"\b{re.escape(term)}\b", text) for term in term_list
    )


def location_ok(job: Job) -> bool:
    """Apply the Ireland / remote-Europe-or-US location rules."""
    loc = f"{job.location}".lower()
    tag_text = " ".join(job.tags).lower()
    haystack = f"{loc} {tag_text}"

    # 1. Anything in Ireland is fine, regardless of arrangement.
    if _has(config.IRELAND_TERMS, haystack):
        return True

    # 2. Not Ireland and not remote -> on-site elsewhere -> drop.
    if not job.remote:
        return False

    # 3. Remote: must be Europe or US (or genuinely global/anywhere).
    # Guard against "Latin America" being read as US "America".
    us_hay = haystack
    for fp in config.US_FALSE_POSITIVES:
        us_hay = us_hay.replace(fp, "")

    if _has(config.EUROPE_TERMS, haystack):
        return True
    if _has(config.US_TERMS, us_hay):
        return True

    # Explicit non-target regions -> drop even if "remote".
    blocked = ["apac", "asia", "latam", "latin america", "india",
               "canada", "australia", "africa", "brazil", "philippines"]
    if _has(blocked, haystack) and not _has(config.EUROPE_TERMS, haystack) \
            and not _has(config.US_TERMS, us_hay):
        return False

    # No country hint but marked remote/worldwide -> keep for review.
    if _has(config.GLOBAL_TERMS, haystack):
        return True

    return False


def matches(job: Job) -> tuple[bool, str]:
    """Return (keep?, reason-if-dropped)."""
    if not _title_included(job.title):
        return False, "title not a frontend/software role"
    if _title_excluded(job.title):
        return False, "title too senior / off-target"
    if not location_ok(job):
        return False, "location outside Ireland / remote-EU-US"
    if _demands_too_much_experience(job.clean_description):
        return False, f"asks for >= {config.MAX_YEARS_EXPERIENCE} years"
    return True, ""
