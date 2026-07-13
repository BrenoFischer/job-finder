# job-finder

A tiny, **free** tool that gathers open software/frontend roles matching my
criteria every day and writes a clickable list I can work through later.

- Runs on a **GitHub Actions cron** (daily at 07:00 UTC).
- Pulls from free job APIs: Remotive, RemoteOK, Arbeitnow, Jobicy, The Muse,
  and Adzuna (Ireland).
- Filters by title, seniority (~3 yrs), and location rules.
- **Deduplicates** against `seen.json`, so a role only ever shows up once.
- Output lands in [`latest.md`](latest.md) and dated files under
  [`jobs/`](jobs/).

## Location rules

| Situation | Kept? |
|-----------|-------|
| Job in Ireland (remote / hybrid / on-site) | ✅ |
| Remote job in Europe or the US (or worldwide) | ✅ |
| On-site/hybrid outside Ireland | ❌ |
| Remote job restricted to APAC / LATAM / India / Canada / etc. | ❌ |

## Setup

1. Push this folder to a new GitHub repo.
2. (Optional but recommended) Add Adzuna keys for Ireland coverage:
   - Register free at <https://developer.adzuna.com/>.
   - Repo → **Settings → Secrets and variables → Actions** → add
     `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`.
   - Without them, the tool still runs on the keyless sources.
3. The workflow runs daily. Trigger it manually from the **Actions** tab
   (**Daily job finder → Run workflow**) to test.

## Tuning

All the knobs live in [`config.py`](config.py): title keywords to include /
exclude, location terms, and the max years-of-experience threshold.

## Run locally

```bash
pip install -r requirements.txt
# optional: set ADZUNA_APP_ID / ADZUNA_APP_KEY in your environment
python main.py
```
