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
