# Scheduling job-scout

job-scout never schedules itself. You create the scheduled task yourself, in the app that runs your Claude Code tasks. This page says what to put in it.

## Cron expression

Use a cron expression with an explicit time zone, in the same IANA zone as `timezone` in `profile/preferences.yaml`:

    CRON_TZ=Australia/Sydney 0 6-16/2 * * 1-5

That runs at 06:00, 08:00, 10:00, 12:00, 14:00 and 16:00, Monday to Friday, Sydney time. Use `Australia/Brisbane` for Queensland.

With `alert_mode: instant_plus_digest` the 17:00 digest needs a run at 17:00 too. List the hours instead:

    CRON_TZ=Australia/Sydney 0 6,8,10,12,14,16,17 * * 1-5

Notes:
- Some schedulers only allow hourly or slower runs, and may start a few minutes late. `run_window.grace_minutes` (default 10) covers a late 17:00 run.
- A digest slot (12:00 or 17:00) is sent by the first run at or after it that has not sent it yet, so a missed run is picked up by the next one.
- Fewer runs means fewer emails. `per_run` mode emails only when there are new matches.
- The skill checks the time itself (`scripts/run_window.py`) and exits quietly outside the window. This is a safety net, not a replacement for the right cron time zone.

## Daylight saving caveat

Sydney changes clocks (AEST UTC+10, AEDT UTC+11, switching on a Sunday in April and October). Brisbane does not.

- If the scheduler supports `CRON_TZ`, it follows the change and runs stay at 06:00 local. Use it.
- If it only supports UTC, the runs shift by one hour local time twice a year. A cron fixed to 19:00 UTC is 06:00 in summer (AEDT) but 05:00 in winter (AEST). The skill then exits quietly for runs that land outside 06:00-17:00 and the first run of the day arrives late or early. Edit the UTC cron when the clocks change, or list extra hours and rely on the window check.
- The change happens on Sunday, so weekday runs are not caught in the missing or repeated hour.
- `zoneinfo` needs the `tzdata` package in a minimal environment (see below).

## Fresh environment on every run

Scheduled runs start in a fresh container with nothing installed. Put this in the environment's **setup script** so it runs before each session:

    pip install python-docx pyyaml tzdata
    # Agent Reach (optional, preferred LinkedIn jobs source). Install from the GitHub archive:
    # the "agent-reach" name on PyPI is an unrelated package.
    pip install https://github.com/Panniantong/agent-reach/archive/main.zip
    agent-reach install --env=auto
    agent-reach doctor || true

Check the current Agent Reach README before relying on those commands; channel names and setup change between releases. Its LinkedIn channel may need a logged-in session. job-scout never logs in, so if the channel is not usable without one, the run falls back to public career pages and job boards and says so in `job-application/last-run.md`. With no Agent Reach, everything still works through web search.

Profile files (`profile/preferences.yaml`, `profile/resumes/`) are git-ignored, so they are not in a fresh clone. Keep them somewhere the scheduled environment can read (for example a private repo or the task's environment files), and never commit them here.
