"""Tunable filters for the job search.

Everything a human might want to tweak lives here so you don't have to touch
the fetching / filtering logic.
"""

# ---------------------------------------------------------------------------
# Title matching
# ---------------------------------------------------------------------------

# A job title must contain at least ONE of these (case-insensitive substring).
INCLUDE_TITLE = [
    "frontend", "front-end", "front end",
    "software developer", "software engineer",
    "web developer", "web engineer",
    "react", "next.js", "nextjs",
    "javascript", "typescript",
    "full stack", "full-stack", "fullstack",
    "ui developer", "ui engineer",
    "react native", "mobile developer",
]

# If the title contains any of these WORDS (whole-word, case-insensitive) the
# job is dropped. Tuned for ~3 years of experience and a frontend/software focus.
EXCLUDE_TITLE_WORDS = [
    # too senior
    "senior", "sr", "staff", "principal", "lead", "director",
    "head", "vp", "chief", "architect", "manager",
    # not the target discipline
    "designer", "devops", "sre", "security", "data scientist",
    "data engineer", "machine learning", "ml engineer",
    "sales", "marketing", "recruiter", "recruiting",
    "product manager", "project manager", "scrum master",
    "account", "support", "solutions engineer", "embedded",
    "electrical", "mechanical", "firmware", "hardware",
]

# ---------------------------------------------------------------------------
# Location rules
#   - Ireland: any arrangement (remote / hybrid / on-site) is fine.
#   - Remote:  must be Europe or the United States (worldwide/anywhere counts).
#   - On-site/hybrid outside Ireland: dropped.
# ---------------------------------------------------------------------------

# NOTE: these are matched as WHOLE WORDS (see filters._has), so short tokens
# like "eu" or "us" only match when they stand alone, not inside other words.
IRELAND_TERMS = [
    "ireland", "irish", "dublin", "cork", "limerick", "galway",
    "waterford", "kilkenny", "sligo", "athlone",
]

EUROPE_TERMS = [
    "europe", "european", "emea", "eu", "eea",
    "uk", "united kingdom", "england", "scotland", "wales",
    "germany", "france", "spain", "portugal", "netherlands",
    "poland", "sweden", "norway", "denmark", "finland", "belgium",
    "austria", "switzerland", "italy", "greece", "romania",
    "czech", "hungary", "lithuania", "latvia", "estonia",
    "cet", "gmt", "bst",
]

US_TERMS = [
    "usa", "united states", "us", "america",
    "est", "pst", "pdt", "edt", "cst",
]

# Remote roles with no country hint at all are treated as open (kept).
GLOBAL_TERMS = ["worldwide", "anywhere", "global", "remote"]

# "America" appears in these, which are NOT the United States -> don't match US.
US_FALSE_POSITIVES = ["latin america", "south america", "central america"]

# ---------------------------------------------------------------------------
# Experience filter
# ---------------------------------------------------------------------------

# Drop a posting whose description clearly asks for this many years or more.
MAX_YEARS_EXPERIENCE = 5

# ---------------------------------------------------------------------------
# Networking
# ---------------------------------------------------------------------------

USER_AGENT = "job-finder/1.0 (personal job search; +https://github.com)"
REQUEST_TIMEOUT = 20  # seconds
