"""Daily job finder.

Fetches roles from several free APIs, filters them to Breno's criteria,
removes anything already seen on a previous run, and writes the new matches
to a dated markdown file plus latest.md.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

import filters
from models import Job
from sources import adzuna, arbeitnow, jobicy, remoteok, remotive, themuse

ROOT = os.path.dirname(os.path.abspath(__file__))
SEEN_PATH = os.path.join(ROOT, "seen.json")
JOBS_DIR = os.path.join(ROOT, "jobs")
LATEST_PATH = os.path.join(ROOT, "latest.md")

SOURCES = [
    ("remotive", remotive.fetch),
    ("remoteok", remoteok.fetch),
    ("arbeitnow", arbeitnow.fetch),
    ("jobicy", jobicy.fetch),
    ("themuse", themuse.fetch),
    ("adzuna", adzuna.fetch),
]

# Keep the seen-file from growing forever.
SEEN_RETENTION_DAYS = 45


def load_seen() -> dict:
    if os.path.exists(SEEN_PATH):
        try:
            with open(SEEN_PATH, encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def prune_seen(seen: dict, today: dt.date) -> dict:
    cutoff = today - dt.timedelta(days=SEEN_RETENTION_DAYS)
    kept = {}
    for key, meta in seen.items():
        try:
            first = dt.date.fromisoformat(meta.get("first_seen", ""))
        except ValueError:
            first = today
        if first >= cutoff:
            kept[key] = meta
    return kept


def collect() -> tuple[list[Job], dict]:
    """Fetch from every source. Returns (jobs, per-source-error-map)."""
    all_jobs: list[Job] = []
    errors: dict[str, str] = {}
    for name, fetch in SOURCES:
        try:
            fetched = fetch()
            all_jobs.extend(fetched)
            print(f"  {name:10s} -> {len(fetched)} raw")
        except Exception as exc:  # one bad API must not kill the run
            errors[name] = str(exc)
            print(f"  {name:10s} -> ERROR: {exc}", file=sys.stderr)
    return all_jobs, errors


def render(jobs: list[Job], today: dt.date, errors: dict) -> str:
    lines = [f"# Job matches - {today.isoformat()}", ""]
    if not jobs:
        lines.append("_No new matching roles today._")
    else:
        lines.append(f"**{len(jobs)} new role(s)** since the last run.")
        lines.append("")
        by_source: dict[str, list[Job]] = {}
        for job in jobs:
            by_source.setdefault(job.source, []).append(job)
        for source in sorted(by_source):
            group = by_source[source]
            lines.append(f"## {source} ({len(group)})")
            lines.append("")
            for job in group:
                tag = " · ".join(t for t in job.tags[:3] if t)
                extra = f" — _{tag}_" if tag else ""
                loc = job.location or ("Remote" if job.remote else "")
                lines.append(
                    f"- [{job.title}]({job.url}) — **{job.company}** "
                    f"({loc}){extra}")
            lines.append("")
    if errors:
        lines.append("---")
        lines.append("### Sources that failed this run")
        for name, msg in errors.items():
            lines.append(f"- `{name}`: {msg}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    today = dt.date.today()
    print(f"Job finder run for {today.isoformat()}")

    seen = load_seen()
    raw, errors = collect()

    # Filter + dedup (both against seen.json and within this run).
    new_jobs: list[Job] = []
    run_keys: set[str] = set()
    kept = dropped = 0
    for job in raw:
        if not job.url or not job.title:
            continue
        ok, _reason = filters.matches(job)
        if not ok:
            dropped += 1
            continue
        kept += 1
        key = job.key()
        if key in seen or key in run_keys:
            continue
        run_keys.add(key)
        seen[key] = {"first_seen": today.isoformat(),
                     "title": job.title, "url": job.url}
        new_jobs.append(job)

    print(f"Matched {kept}, dropped {dropped}, new (unseen) {len(new_jobs)}")

    # Write outputs.
    os.makedirs(JOBS_DIR, exist_ok=True)
    markdown = render(new_jobs, today, errors)
    dated = os.path.join(JOBS_DIR, f"{today.isoformat()}.md")
    with open(dated, "w", encoding="utf-8") as fh:
        fh.write(markdown)
    with open(LATEST_PATH, "w", encoding="utf-8") as fh:
        fh.write(markdown)

    seen = prune_seen(seen, today)
    with open(SEEN_PATH, "w", encoding="utf-8") as fh:
        json.dump(seen, fh, indent=1, sort_keys=True)

    print(f"Wrote {dated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
