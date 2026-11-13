---
name: recruiter-scout
description: Unattended executive-recruiter outreach agent. Finds recruiters, search firms and investor talent partners that place C-level, VP and Head-of roles matching the saved preferences, looks for live-search signals, scores each against the candidate's executive profile, drafts a full outreach pack (email, follow-ups, LinkedIn note, warm-intro ask, call prep) for the best matches, tracks follow-ups due, and emails a short report. Never sends to recruiters. Use for scheduled recruiter-search runs, or when asked to find executive recruiters to contact.
---

# Recruiter Scout

Finds executive recruiters, drafts the outreach, tracks the pipeline, emails a report. The user reviews and sends by hand. This skill runs unattended from a scheduled task, so never stop to ask a question. When something is missing, say so in the report.

Read `references/outreach-playbook.md` before drafting. It holds the message rules, the follow-up cadence and the quality gate.

## Files
- `profile/recruiter-preferences.yaml`: settings (template: `profile/recruiter-preferences.example.yaml`).
- The resume named in `resume_file` (default `profile/resume.md`). The candidate may be someone other than the repo owner.
- `profile/recruiter-tracker.csv`: one row per recruiter. Columns: `name,firm,tier,link,contact_route,score,signal,status,first_reported,last_action,next_action,next_action_date,notes`. Create it if missing. The user edits `status` by hand (`drafted`, `sent`, `replied`, `call_booked`, `in_process`, `closed`, `no_reply`).
- `recruiter-outreach/<date>/<firm>-<recruiter>/`: outputs per drafted recruiter.
- Reuse `.claude/skills/job-scout/scripts/docs_theme.py` for Word files and `.claude/skills/job-application-playbook/prompts.md` for writing prompts.

## Who counts as a target
Only people whose public profile or firm page shows they place roles at the levels in `levels` (C-level, VP, Head-of). Sort each into a tier:
- **Tier A, retained search partners** in the candidate's function and industry (global firms and their practice leads).
- **Tier B, boutique executive search firms** that specialise in the candidate's function, industry or region.
- **Tier C, investor talent partners**: heads of talent and operating partners at PE and VC funds who place leaders into portfolio companies.
- **Tier D, in-house executive recruiters** at companies in `target_companies` or matching `industries`.
- **Tier E, interim and fractional executive firms**, only if `open_to_interim` is true.
Reject contingent volume recruiters, staffing agencies, anyone listing "all levels", anyone whose practice does not match, and anything in `exclude_firms`. If seniority focus cannot be verified from public pages, mark "exec focus unverified" and score it lower. Do not guess.

## Hard rules
- Never send to, message, connect with, or post to any recruiter. Never submit forms, log in, or apply. Outreach is a file or Gmail draft only, and the only address ever emailed is `report_email`.
- Never invent resume facts, titles, numbers, board seats, mutual contacts or placements. Use `[ADD number]` markers for gaps.
- Public pages only. Use only business contact details the recruiter or firm publishes. Never guess email addresses. If none exists, write "no public contact" and give the firm's submission page or profile link.
- Follow `confidentiality` in the settings. Never mention a withdrawn or rescinded offer in any written outreach.
- If a site blocks or fails, name the host in the report and carry on. Do not fake results.

## Run steps
1. **Load.** Read the settings, the resume and the tracker. If settings or resume are missing, create a draft report saying which, and stop.
2. **Follow-ups first.** From the tracker, list every row whose `next_action_date` is today or earlier and whose status is `sent` or `no_reply`. Draft the due follow-up for each (playbook cadence) into that recruiter's folder. Stop following up after the breakup note.
3. **Find signals.** Search for events from the last `signal_window_days` that suggest a live or coming search in the target function and industry: executive departures, funding rounds, PE acquisitions, new-market launches, and "appointed" announcements naming the search firm that ran them. Each signal is a reason to contact a specific recruiter now.
4. **Find recruiters.** Use what works, in order: Agent Reach LinkedIn channel if installed, then web search and public firm pages (practice pages, partner bios, placement announcements, fund team pages). Aim for a mix of tiers. Record: name, firm, tier, title, practice area, region, public contact route, link, evidence of seniority focus (quote or page), recent placements, and any linked signal.
5. **Clean.** Drop duplicates, anyone already in the tracker, wrong region, `exclude_firms`, `exclude_words` matches, and anyone failing the target test.
6. **Score out of 10.** Practice match to role and industry 35%, seniority focus evidence 20%, live signal or recent relevant placement 20%, region 10%, reachable contact route 15%. Output score, one-line reason, verified or unverified. If only a snippet was reachable, say "snippet only".
7. **Pick.** Take scores at least `min_fit_score`, best first, up to `max_drafts_per_run`, with at most two from the same firm.
8. **Draft the pack** for each pick, following the playbook:
   - `outreach-email.md`: the first email.
   - `follow-ups.md`: follow-up 1, follow-up 2 and the breakup note, each with its send-after date.
   - `linkedin-note.md`: connection note under 300 characters.
   - `warm-intro-ask.md`: a short note the candidate can send to a mutual contact asking for an introduction, plus the instruction "check LinkedIn for shared connections at <firm> before sending cold".
   - `call-prep.md`: what this recruiter covers, three questions to ask them, and the candidate's answers to the standard recruiter questions listed in the playbook, with `[ADD]` markers where the resume is silent.
   - One shared `exec-bio.md` in `recruiter-outreach/` (build once, reuse), plus Word via `docs_theme.py` when supported.
   Run the playbook quality gate on every draft. Fix or drop drafts that fail.
9. **Update the tracker.** Add new rows with status `drafted`. Set `next_action` and `next_action_date` for every row touched.
10. **Report.** One email. Subject: `Recruiter scout: N new, M drafted, F follow-ups due (<date>)`. Body, plain and short:
    - Top line: counts, pipeline totals by status, and anything that failed.
    - **Do today**: follow-ups due, then new drafts, best first.
    - Per drafted recruiter: name, firm, tier, link, contact route, score, why they fit, the signal if any, evidence of seniority focus, files attached.
    - Other matches below the cut-off: name, firm, link, score.
    - Reminder: check for a warm introduction first, fill `[ADD]` markers, send by hand, then set status to `sent` in the tracker.
    Use `email_mode`: `draft` creates a Gmail draft to `report_email`, `send` emails `report_email`. Never any other address.
11. **Nobody found?** One-line report with what was searched and what failed. Still report follow-ups due.

## Done when
The report exists in Gmail, drafted recruiters have their packs attached, and the tracker is updated.
