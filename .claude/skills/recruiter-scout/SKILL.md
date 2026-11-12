---
name: recruiter-scout
description: Unattended executive-recruiter outreach agent. Finds recruiters and search firms that exclusively or primarily place C-level roles (CEO, CFO, COO, CTO, CMO, CIO, CHRO, CPO and similar) matching the user's saved preferences, scores each against the user's executive profile, drafts a tailored outreach email and executive bio for the best matches, and emails a short report. Never sends to recruiters. Use for scheduled recruiter-search runs, or when asked to find executive recruiters to contact.
---

# Recruiter Scout

Finds executive recruiters, drafts the outreach, emails a report. The user reviews and sends by hand. This skill runs unattended from a scheduled task, so never stop to ask a question. When something is missing, say so in the report.

## Files
- `profile/recruiter-preferences.yaml`: search settings (template: `profile/recruiter-preferences.example.yaml`).
- `profile/resume.md`: master resume. For C-level, lead with scope: P&L, headcount, board exposure, transformations.
- `profile/recruiters-seen.json`: recruiters already reported (by name + firm, or profile link). Create it if missing.
- `recruiter-outreach/<date>/<firm>-<recruiter>/`: outputs for each drafted recruiter.
- Reuse `.claude/skills/job-scout/scripts/docs_theme.py` for Word files and `.claude/skills/job-application-playbook/prompts.md` for the writing prompts.

## What counts as a target
Only people whose public profile or firm page shows they **exclusively or mainly place C-level / board / executive-committee roles**. Typical sources: retained executive search firms (Spencer Stuart, Russell Reynolds, Korn Ferry, Heidrick & Struggles, Egon Zehnder, Boyden, and boutiques), and individual partners on those firms' pages. Reject:
- Contingent or volume recruiters, staffing agencies, and anyone listing mid-level or "all levels" roles.
- Anyone whose practice (industry or function) does not match `target_roles` or `industries`.
- Firms or people in `exclude_firms`.
If exclusivity cannot be verified from public pages, mark "exec focus unverified" and score it lower. Do not guess.

## Hard rules
- Never send to, message, connect with, or post to any recruiter. Never submit forms, log in, or apply. Outreach is a **Gmail draft or file only**, and the only address that is ever emailed is `report_email`.
- Never invent resume facts, titles, numbers, board seats or mutual contacts. Use `[ADD number]` markers for gaps.
- Public pages only. Use only business contact details the recruiter publishes themselves (firm page, submission page). Never guess email addresses or scrape personal data. If no public contact route exists, say "no public contact" and give the firm's submission page or profile link instead.
- Keep confidentiality in mind: executives job-hunt quietly. Outreach drafts must not mention the user's current employer's internal information, and reports go only to the user's own address.
- If a site blocks or fails, name the host in the report and carry on. Do not fake results.

## Run steps
1. **Load settings.** Read `profile/recruiter-preferences.yaml` and `profile/resume.md`. If either is missing, create a draft report saying which, and stop.
2. **Find recruiters.** In order, use what works:
   a. Agent Reach (`agent-reach` skill) LinkedIn channel, if installed.
   b. Web search and public firm pages: "<firm> <function> practice partner", "retained executive search <industry> <region> CFO", firm "people" and "practices" pages, and recent placement announcements (these also show who is actively hiring).
   Record: name, firm, title, practice area (function and industry), region, public contact route, link, evidence of C-level focus (quote or page), recent C-level placements or open searches if public.
3. **Clean the list.** Drop duplicates, anyone in `recruiters-seen.json`, `exclude_firms`, wrong region (outside `regions`), and anyone failing the "what counts" test above.
4. **Triage (all remaining).** Score fit out of 10: practice match to target role and industry (40%), C-level exclusivity evidence (25%), region match (15%), seniority and activity of recent placements (20%). Output: score, one-line reason, exec-focus verified or unverified. If only a snippet was reachable, say "snippet only".
5. **Pick drafts.** Take recruiters scoring at least `min_fit_score`, best first, up to `max_drafts_per_run`.
6. **Draft (picked only).** For each, write into the output folder:
   - `outreach-email.md`: under 150 words. Subject line, who the user is in one line (title, scope, sector), two proof points from the resume with real numbers, the roles and industries they want, location and availability, discreet-search note, one clear ask (a 20-minute intro call). Reference one specific, true fact about the recruiter's practice or a recent placement. No flattery, no attachment spam.
   - `linkedin-note.md`: under 300 characters connection note.
   - `exec-bio.md`: one-page executive bio from the resume (scope, results, board and advisory, education), only if `profile/exec-bio.md` does not already exist. Build Word with `python3 .claude/skills/job-scout/scripts/docs_theme.py --resume <exec-bio.md> --out-dir <folder> --prefix <Name>` when supported.
7. **Report.** One email. Subject: `Recruiter scout: N new recruiters, M drafted (<date>)`. Body, plain and short:
   - Top line: counts and anything that failed (hosts blocked, channels missing).
   - Per drafted recruiter: name, firm, link, practice area, public contact route, score, why they fit, evidence they place C-level, and which files are attached.
   - Short list of other matches below the cut-off: name, firm, link, score.
   - What to do: review, fill `[ADD number]` markers, then send or connect by hand.
   Use `email_mode`: `draft` creates a Gmail draft to `report_email`, `send` emails `report_email`. Never any other address.
8. **Remember.** Append every reported recruiter to `profile/recruiters-seen.json`.
9. **Nobody found?** One-line report saying so, with what was searched and what failed.

## Done when
The report exists in Gmail, drafted recruiters have outreach files attached, and `recruiters-seen.json` is updated.
