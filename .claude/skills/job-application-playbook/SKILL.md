---
name: job-application-playbook
description: Runs the 17-prompt AI-Powered Job Application Playbook end to end for one job. Takes a resume, LinkedIn profile and job description, researches the company and hiring manager, scores fit, then writes a tailored cover letter and resume. Use when the user wants to apply for a job, tailor a resume or cover letter to a JD, or runs /job-application-playbook.
---

# Job Application Playbook

Runs 17 chained prompts in one session. Each output feeds the next. The full text of every prompt is in `prompts.md` (same folder). Read it before starting and use the prompts as written, filling in the user's materials.

## Rules that never bend
- Run the prompts in order, 1 to 17. Never skip Prompt 2.
- Prompt 2 needs live web research. Use WebSearch/WebFetch. If neither works, tell the user and stop at that point instead of inventing the brief.
- Flag every assumption in research as INFERRED. Name real companies, programs, dates.
- Never invent resume facts, numbers, employers or titles. Everything in the letter and resume must trace to the user's materials.
- Keep all outputs in one working folder so each step can read the earlier ones.

## Setup
1. Ask for the three inputs if missing: resume, LinkedIn profile (text or URL), job description (text or URL). Accept file paths, pasted text or URLs.
2. Create `./job-application/<company>-<role>/` and save the inputs as `00-inputs.md`.
3. Prompt 1: confirm all three were read, in two lines. Then continue.

## Pipeline

| Stage | Prompts | Save as | Pause for user? |
|---|---|---|---|
| 01 JD Analysis | 1 Load, 2 Trigger Intelligence, 3 HM Attraction Profile, 4 The Real Ask | `01-jd-analysis.md` | No |
| 02 Fitment | 5 Fit table, 6 Fit report, 7 Mountain of Value | `02-fitment.md` | Yes, show score and winning angle |
| 03 Cover letter | 8 Draft, 9 Format, 10 Align, 11 Final read | `03-cover-letter.md` | No |
| 04 Resume | 12 Title, 13 Summary, 14 Capabilities, 15 Experience, 16 Structure check, 17 Final alignment | `04-resume.md` | Yes at Prompt 12 (pick a title) |

## How to run each prompt
- Print a one-line header: `Prompt N of 17: <name>`.
- Apply the prompt to the materials plus every earlier output. Prompt 8 uses the Mountain of Value (7) and the Real Ask (4). Prompt 10 reads the letter against the JD analysis. Prompts 13 to 17 use the fit report and the title chosen at 12.
- Show the output, short. Do not add commentary the prompt did not ask for.
- Prompt 9 is a formatting spec. Apply it when producing the letter file.
- Prompt 12 gives 3 options. Wait for the user to choose.
- Prompt 16 flags issues only. Prompt 17 returns a short change list. Apply only changes the user accepts.

## Gates
- After stage 02, show the fit score, gaps and winning angle. If the score is under 5/10, say so plainly and ask whether to continue.
- If a prompt's rules conflict with the user's facts (for example, fewer than 2 numbers exist for Prompt 15), say so. Do not make numbers up.

## Finish
Write the final files to the folder: `cover-letter.md` and `resume.md` (offer .docx via the docx skill if the user wants Word). End with a 5-line summary: fit score, winning angle, chosen title, files written, open assumptions to verify.
