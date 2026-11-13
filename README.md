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

## Recruiter scout (executive outreach)
`/recruiter-scout` is a second agent built like the job scout. It finds recruiters, search firms and investor talent partners that place C-level, VP and Head-of roles, looks for signs of a live search, scores each one, drafts an outreach pack (email, three follow-ups, LinkedIn note, warm-intro ask, call prep), tracks follow-ups due, and emails you a report. It never contacts a recruiter itself. You review and send by hand.

- Settings: copy `profile/recruiter-preferences.example.yaml` to `profile/recruiter-preferences.yaml`.
- Skill: `.claude/skills/recruiter-scout/SKILL.md`
- Message rules, cadence and offer-protection checklist: `.claude/skills/recruiter-scout/references/outreach-playbook.md`
- Pipeline: `profile/recruiter-tracker.csv` (you update the status after sending)
- Outputs: `recruiter-outreach/<date>/<firm>-<recruiter>/`
