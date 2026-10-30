---
name: job-scout
description: Unattended job scout. Searches for new job openings from the last 24 hours that match the user's saved preferences, scores each against their resume, drafts a tailored resume and cover letter for the best matches using the job-application-playbook, and emails a short report. Never applies. Use for scheduled job-search runs, or when asked to find new jobs and prepare applications.
---

# Job Scout

Finds new jobs, drafts the paperwork, emails a report. The user reviews and applies by hand. This skill runs unattended from a scheduled task, so never stop to ask a question. When something is missing, say so in the report.

## Files
- `profile/preferences.yaml`: the user's search settings (template: `profile/preferences.example.yaml`).
- `profile/resume.md`: master resume (format: `references/resume-format.md`).
- `profile/seen.json`: job links already reported. Create it if missing.
- `job-application/<date>/<company>-<role>/`: outputs for each drafted job.
- `scripts/docs_theme.py`: builds the Navy & Ice Word files.
- The playbook prompts: `.claude/skills/job-application-playbook/prompts.md`.

## Hard rules
- Never apply to a job, submit a form, log in anywhere, post, message, or send to anyone except `report_email`.
- Never invent resume facts, employers, titles or numbers. Use `[ADD number]` markers for gaps.
- Read public pages only. If a site blocks or fails, name the host in the report and carry on. Do not fake results.
- Only report a job as "new in the last 24 hours" when its posted date shows that. Otherwise label it "date unverified".
- No attachments of other people's data. Reports go to the user's own address.

## Run steps

1. **Load settings.** Read `profile/preferences.yaml` and `profile/resume.md`. If either is missing, create a draft report saying which file is missing, and stop.
2. **Find jobs.** Try sources in this order and use what works:
   a. Agent Reach (`agent-reach` skill), LinkedIn jobs channel, if installed. Search each title and location for the last 24 hours (check what filter it supports, do not assume).
   b. Web search and public company or job-board pages for each title, location and work mode.
   Record for each job: title, company, location, link, posted date (or "unverified"), pay if shown, short description.
3. **Clean the list.** Drop jobs already in `seen.json`, duplicates, jobs outside the location or work mode, jobs whose text matches an `exclude_words` or `exclude_companies` entry, and jobs under `min_monthly_pay` when pay is shown. Keep jobs with no pay shown and mark pay "not listed".
4. **Triage (all remaining jobs).** Playbook prompts 1, 5 and 6 only, in short form. Read the full job description when reachable. Output per job: fit score out of 10, three strengths, the main gaps. If only a snippet was reachable, say "snippet only" and cap the score confidence at "rough".
5. **Pick drafts.** Take jobs scoring at least `min_fit_score`, best first, up to `max_drafts_per_run`.
6. **Draft (picked jobs only).** Run the trimmed playbook: prompts 2, 3, 4, 7, then cover letter 8, 10, 11, then resume 13, 14, 15, 17. Skip 9 (the template formats it), 12 (choose the best-matching title yourself, honest to the user's history), and 16 (the template controls length). Skip prompt 2's web research for a job that has no company information and say so. Write `resume.md` and `cover-letter.md` for the job, then build Word files:
   `python3 .claude/skills/job-scout/scripts/docs_theme.py --resume <resume.md> --letter <cover-letter.md> --out-dir <job folder> --prefix <Name>`
7. **Report.** Build one email. Subject: `Job scout: N new matches, M drafted (<date>)`. Body, plain and short:
   - Top line: counts and anything that failed (hosts blocked, channels not installed).
   - Per drafted job: title, company, link, posted date, pay, fit score, why it fits, gaps, and which files are attached.
   - A short list of other matches below the cut-off: title, company, link, score.
   - What to do: review, edit any `[ADD number]` marker, apply by hand.
   Attach each drafted job's Word files so they survive after this session ends. Use `email_mode`: `draft` creates a Gmail draft, `send` emails `report_email`. Only ever `report_email`.
8. **Remember.** Append every reported job link to `profile/seen.json`.
9. **No jobs found?** Send a one-line report saying so, with what was searched and what failed.

## Done when
The report exists in Gmail, drafted jobs have Word files attached, and `seen.json` is updated.
