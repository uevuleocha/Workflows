# Issue And Review Templates

Use these shapes without inventing missing facts. Omit a section only when it is genuinely irrelevant and the omission cannot hide an evidence gap.

## Issue Draft

```markdown
Repository: `OWNER/REPO`

Proposed title: [specific symptom, affected component, and condition]

Proposed body:

### Environment

- Version/build/commit: [value]
- Platform: [value]
- Relevant configuration: [sanitized value]
- Restart/reload boundary: [value]

### Summary

[Concise defect statement and impact.]

### Steps to reproduce

1. [Step]
2. [Step]
3. [Step]

### Expected behavior

[Expected result.]

### Actual behavior

[Observed result.]

### Evidence

[Current, sanitized evidence with facts separated from inference.]

### Additional context

[Workaround, regression boundary, or one-line cross-project reference when relevant.]
```

## Ordinary Review Gate

```markdown
## OWNER/REPO

[Exact issue draft]

Nothing has been posted. Please explicitly approve this exact title and body for filing, or tell me what to amend.
```

Do not accept a vague continuation phrase as approval. A revision returns to this gate.

## Duplicate-Found Stop

```markdown
## OWNER/REPO - duplicate decision

### Matches found

- `#NUMBER` - STATE - TITLE - created YYYY-MM-DD (AGE) - URL

### OG Bug Report

`#NUMBER` is the OG Bug Report because [type-classification evidence] and it is the earliest-created eligible defect report. [Mention a narrow later-canonical conflict when one exists.]

### New-issue draft

[Exact, unchanged issue title and body]

### OG comment draft

Additional evidence for this report: [only the new reproduction, version confirmation, affected configuration, corrected mechanism, or other information the thread lacks].

Nothing has been posted. For this issue, reply `file it anyway` to publish the new-issue draft, or `post the comment` to publish the OG comment draft. You may also request changes or choose to post nothing.
```

All four parts must appear in the same turn: matches, named OG Bug Report, unchanged new-issue draft, and ready-to-post comment draft. The two publication choices must be answerable in one reply.

If the new material adds nothing, keep both drafts visible but say: `The proposed comment adds no material evidence that the OG thread lacks. I recommend posting nothing.`

## Multi-Repository Review

Give every repository its own heading and decision line. Never combine approval across repositories implicitly. A concise answer may approve different outcomes explicitly, for example:

```text
OWNER/A: file it anyway
OWNER/B: post the comment
OWNER/C: do not post
```

