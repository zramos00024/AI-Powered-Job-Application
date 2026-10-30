# AI-Powered Job Application

A Claude Code skill that runs the 17-prompt AI-Powered Job Application Playbook (Sasank Namburi) end to end: it researches the company and hiring manager, scores your fit, then writes a tailored cover letter and resume.

## Use it
Open this repo in Claude Code and run `/job-application-playbook`. Give it your resume, LinkedIn profile and the job description. Each stage is saved to `job-application/<company>-<role>/`.

- Prompts run in order, 1 to 17. Prompt 2 needs web search and is never skipped.
- It pauses after Fitment to show your score, and at Prompt 12 for you to pick a resume title.
- It never invents resume facts or numbers.

## Contents
- `.claude/skills/job-application-playbook/SKILL.md`: the workflow
- `.claude/skills/job-application-playbook/prompts.md`: full text of all 17 prompts
- `visualizer/index.html`: open in a browser to watch a sample run of the pipeline (fictional data)

## Job scout (unattended)
`/job-scout` finds new jobs, drafts a resume and cover letter for the best matches, and sends a short alert. It never applies, logs in or messages anyone.

- **Setup:** copy `profile/preferences.example.yaml` to `profile/preferences.yaml`. Put your sample resumes in `profile/resumes/`, one per role type, each starting with a `Role family / Target titles / Keywords` header. Placeholder examples are in `profile/resumes.example/`. `profile/` is git-ignored, so resumes, preferences and outputs stay private.
- **Resume choice:** for each job, `scripts/pick_resume.py` scores every sample by title and keyword overlap. The report names the sample used and why. If none is close enough, the job is listed with "no close resume" and no draft.
- **Formatting:** `output_mode: navy_ice` rebuilds from markdown. `output_mode: keep_layout` edits your own `.docx` in place (text only, paragraph for paragraph; it refuses links, fields, images and big length changes, and falls back to Navy & Ice).
- **Run window:** `timezone` (for example `Australia/Sydney`), weekdays 06:00-17:00, `max_drafts_per_run`. Outside the window the skill exits quietly.
- **Alerts:** `per_run` (default, quietest: one email per run, only when there are new matches) or `instant_plus_digest`.
- **Sources:** Agent Reach's LinkedIn jobs channel if installed, else career pages and job boards. Posted dates are only trusted when shown; otherwise jobs are labelled "date unverified".
- **Scheduling:** nothing is scheduled for you. See [docs/SCHEDULING.md](docs/SCHEDULING.md) for the cron expression, daylight saving, and the setup script for a fresh environment.
- **Tests:** `python3 -m unittest discover -s .claude/skills/job-scout/tests -v`

Contents add: `.claude/skills/job-scout/` (skill, scripts, tests), `docs/SCHEDULING.md`, `profile/resumes.example/`.
