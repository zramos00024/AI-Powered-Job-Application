---
name: job-scout
description: Unattended job scout. Inside the user's run window (timezone and hours), searches for new job openings matching their saved preferences, scores each against their sample resumes, drafts a tailored resume and cover letter for the best matches using the closest sample and the job-application-playbook, and sends a short alert. Never applies. Use for scheduled job-search runs, or when asked to find new jobs and prepare applications.
---

# Job Scout

Finds new jobs, drafts the paperwork, sends a short alert. The user reviews and applies by hand. This skill runs unattended from a scheduled task, so never stop to ask a question. When something is missing, say so in the report. The skill never creates its own schedule: see `docs/SCHEDULING.md`.

## Files
- `profile/preferences.yaml`: search, run window, alert and output settings (template: `profile/preferences.example.yaml`).
- `profile/resumes/*.md`: sample resumes, one per role type, each with a header block (format: `references/resume-format.md`). Optional matching `.docx` for `output_mode: keep_layout`.
- `profile/seen.json`: job links already reported. Create it if missing.
- `profile/state.json`: digest slots already sent today (managed by `scripts/run_window.py`).
- `profile/pending.json`: matches waiting for the next digest (`instant_plus_digest` only). Create it if missing.
- `job-application/<date>/<company>-<role>/`: outputs for each drafted job. `job-application/last-run.md`: the latest run log.
- `scripts/run_window.py`, `scripts/pick_resume.py`, `scripts/docs_theme.py`, `scripts/docx_inplace.py`. Tests: `tests/test_scout.py`.
- The playbook prompts: `.claude/skills/job-application-playbook/prompts.md`.

## Hard rules
- Never apply to a job, submit a form, log in anywhere, post, message, or send to anyone except `report_email`. If a source (including an Agent Reach channel) needs a login, skip that source and name it in the log.
- Never invent resume facts, employers, titles or numbers. Tailor a sample using only the facts in it. Mark gaps `[ADD number]`.
- Read public pages only. If a site blocks or fails, name the host in the report and carry on. Do not fake results.
- Only call a job "new in the last 24 hours" when its posted date shows that. Otherwise label it "date unverified". Never claim a date filter worked unless the results prove it.
- No emails outside the run window. No attachments of other people's data. Reports go to the user's own address.

## Run steps

0. **Run window gate.** Run `python3 .claude/skills/job-scout/scripts/run_window.py`. Exit code 10 means outside the window (wrong hours, weekend, or timezone not set up): stop at once, silently, with no search, no email, no files. Exit 0 prints `digest_due` (a slot such as `12:00`, or null). If `profile/preferences.yaml` is missing, write `job-application/last-run.md` saying so and stop.
1. **Load settings.** Read `profile/preferences.yaml`. List `resumes_dir`. If there are no sample resumes, log which is missing and stop.
2. **Find jobs.** Use the first source that works:
   a. Agent Reach (`agent-reach` skill), LinkedIn jobs channel, if installed (`agent-reach doctor` shows channel health). Search each title and location. Check what date filter it really supports and only trust returned posted dates.
   b. Web search and public career pages and job boards for each title, location and work mode.
   Record for each job: title, company, location, link, posted date (or "date unverified"), pay if shown, short description.
3. **Clean the list.** Drop jobs already in `seen.json`, duplicates, jobs outside the location or work mode, jobs whose text matches an `exclude_words` or `exclude_companies` entry, and jobs under `min_monthly_pay` when pay is shown. Keep jobs with no pay shown and mark pay "not listed".
4. **Pick the resume for each job.** Save the job description to a temp file and run
   `python3 .claude/skills/job-scout/scripts/pick_resume.py --resumes-dir <resumes_dir> --job-title "<title>" --jd-file <file> --min-score <min_resume_match_score>`.
   It compares the job against every sample by title and keyword overlap. Read the ranked list yourself too: if the script's winner looks wrong for the job, say so and pick the better one, naming why. If `match` is null, no sample is close enough: do not force one. List the job as "no close resume" with the best score, and do not draft it.
5. **Triage (all remaining jobs).** Playbook prompts 1, 5 and 6 only, in short form, using the chosen sample as the resume. Read the full job description when reachable. Output per job: fit score out of 10, three strengths, the main gaps. If only a snippet was reachable, say "snippet only" and treat the score as rough.
6. **Pick drafts.** Jobs scoring at least `min_fit_score` with a matched resume, best first, up to `scoring.max_drafts_per_run`. The rest are listed, not drafted.
7. **Draft (picked jobs only).** Run the trimmed playbook with the chosen sample as the source of facts: prompts 2, 3, 4, 7, then cover letter 8, 10, 11, then resume 13, 14, 15, 17. Skip 9, 12 (choose the best honest title yourself, from the sample's target titles) and 16. Skip prompt 2's web research for a job with no company information and say so. Write the tailored `resume.md` (without the header block) and `cover-letter.md` in the job folder, then build files by `output_mode`:
   - `navy_ice`: `python3 .claude/skills/job-scout/scripts/docs_theme.py --resume <resume.md> --letter <cover-letter.md> --out-dir <job folder> --prefix <Name>`
   - `keep_layout`: needs `<sample-name>.docx` beside the sample. Run `scripts/docx_inplace.py dump <sample.docx>`, write an edits JSON that maps paragraph index to new text for the paragraphs that change (a list of strings for mixed-format paragraphs), then `scripts/docx_inplace.py apply <sample.docx> <edits.json> <job folder>/<Name>-Resume.docx`. The tool changes text only and refuses unsafe edits (see its docstring). If the .docx is missing or `apply` refuses, build the Navy & Ice resume instead and say so in the report. Build the cover letter with `docs_theme.py --letter`.
8. **Alert.** Follow `alerts.alert_mode`. Keep every email short: subject, a top line, then per job one or two lines.
   - Subject: `Job scout: N new matches, M drafted (<date>)`. Digest: `Job scout digest <HH:MM>: N matches`.
   - Per drafted job: title, company, link, posted date or "date unverified", pay, fit score, **resume used and why**, main gaps, files attached (note any `[ADD number]` markers). Other matches: title, company, link, score. Jobs with no close resume: title, link, best score. At most `max_jobs_listed_per_email` jobs; say how many were left out.
   - **per_run** (default): if there are no new matches, send nothing. Otherwise send one email.
   - **instant_plus_digest**: jobs scoring at least `instant_min_score` go in one immediate email this run. Other new matches are appended to `profile/pending.json`. If `digest_due` is set and `pending.json` is not empty, send one digest of it, empty the file, then run `run_window.py --mark-digest-sent <slot>`. If `digest_due` is set and nothing is pending, mark it sent and send nothing.
   - Never send more than `max_emails_per_run` emails in a run.
   - Use `email_mode`: `draft` creates a Gmail draft, `send` emails `report_email`. Only ever `report_email`. Attach each drafted job's Word files.
9. **Remember and log.** Append every reported job link to `profile/seen.json`. Write `job-application/last-run.md`: time, sources used, hosts blocked, channels missing, counts. Failures go here, not in an extra email.

## Done when
Inside the window: the log exists, alerts follow the chosen mode, drafted jobs have files attached, and `seen.json` is updated. Outside the window: nothing happened.
