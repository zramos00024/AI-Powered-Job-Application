# resume.md / cover-letter.md format (read by scripts/docs_theme.py)

## Sample resumes (profile/resumes/*.md)
One file per role type. A header block comes first, above the `# Name` line. `pick_resume.py` reads it; `docs_theme.py` ignores it.

    Role family: Head of Support
    Target titles: Head of Support; Director of Customer Support
    Keywords: support strategy, team leadership, escalation management, SLA

Titles and keywords are separated by `;` or `,`. Keep keywords to real skills the sample backs up. Working examples (placeholder data): `profile/resumes.example/`.
For `output_mode: keep_layout`, put the candidate's own `.docx` next to the sample with the same file name (`head-of-support.docx`).

## Tailored resume.md

resume.md must follow this exact shape or the .docx builder will mis-style it:

    # Full Name
    +63 000 000 0000 | email@example.com | City, Country

    ## <Resume title, 4-8 words>

    ## Summary
    Two to four sentences. No numbers.

    ## Core Capabilities
    Label | Label | Label
    Label | Label | Label

    **Key Technologies:** Tech · Tech · Tech

    ## Professional Experience

    **Job Title** | Employer | Dates | Location
    - One-sentence bullet, under 20 words.

    ## Education
    Degree, School, Year

Rules: the line right under the name is the contact line. The first `##` line is the title. Job lines start with `**`, use ` | ` between parts, and are followed by `- ` bullets.

cover-letter.md: plain paragraphs separated by one blank line. The last paragraph is the sign-off ("Regards,\nName"). No header block, since the .docx adds the two-tone strip.
