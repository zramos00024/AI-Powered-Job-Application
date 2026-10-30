# resume.md / cover-letter.md format (read by scripts/docs_theme.py)

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
