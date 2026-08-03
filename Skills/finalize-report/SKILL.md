---
name: finalize-report
description: Finalize an existing pending report after verifying completion evidence, update its dismissible footer to REPORTED, rename its suffix, and move it from Live Reports to Historical Reports while preserving its permanent number. Use when the user asks to finalize, close, mark reported, sent, or read a pending report.
---

# Finalize Report

Close an existing pending report as `reported`. This skill never creates,
updates, or reopens a report; route those requests to `report-this`.

```text
From: <root>\Archive\Live\Reports\<Subject>\N.) <Topic>_pending.md
To:   <root>\Archive\Historical\Reports\<Subject>\N.) <Topic>_reported.md
```

Terminal state is always `reported`, regardless of report mode and regardless of
whether the user sent the report externally or read/accepted it personally.

## Project Contract

Follow the workspace's canonical contract. Preserve UTF-8, user data, approval
gates, and public-repository safety rules.

## Invocation

Treat these as direct invocation:

- `/finalize-report` or `use finalize-report`
- `finalize report`, `close this report`, or `mark this report reported`
- direct confirmation such as `I've sent it` or `I've read it, close it` when a
  pending report is clearly referenced

Requests to create, revise, extend, or reopen route to `report-this`.

## Target Selection

Use the user-referenced pending report. Otherwise scan recursively under
`Archive\Live\Reports\` for `_pending.md` files. Use the sole clear match; ask
when multiple reports are plausible; stop when none exists.

Never finalize a report already under Historical or one ending `_reported.md`.
Reopening belongs to `report-this`.

## Completion Evidence

Do not rubber-stamp. Finalize only with at least one valid evidence route:

- direct user confirmation that the report was sent, read, accepted, or should
  be closed
- current-session or durable evidence that its stated purpose is complete
- satisfaction of an embedded Prompt Contract, when one exists

If the report contains a Prompt Contract, review each DEFINITION OF DONE item
and every FAILURE condition. Every DoD item must be satisfied or explicitly
deferred by the user, and no unwaived FAILURE condition may remain active.

If evidence is partial or ambiguous, stop and ask. A report's age, existence,
polish, or location is not completion evidence.

## Finalization Procedure

1. Read the pending report and preserve its full body and created date.
2. Count canonical dismissible footers. Require exactly one. If the footer is
   missing or duplicated, stop before changing lifecycle state, suffix, path, or
   content; route footer repair through `report-this`.
3. Record the original Live path and derive the Historical path using the same
   unnumbered Subject, permanent `N.)` prefix, and title; change only
   `_pending.md` to `_reported.md`.
4. Create the matching Historical Subject folder when allowed.
5. Stop if the target filename exists or if its number collides with another
   Historical report. Never overwrite, delete, or renumber.
6. Replace only the one canonical dismissible footer lifecycle line with:
   `**Report lifecycle:** REPORTED ✅ — created <date>, reported <today>.`
   Keep the footer fencing and delete-before-sending instruction intact. Do not
   add a mode tag or top lifecycle header.
7. Move the file Live to Historical as a true move. Leave no duplicate in Live.
8. Verify the final path, suffix, footer, number, Subject, body preservation,
   absence of the Live source, and UTF-8.

## File And Number Rules

- Subject folders are never numbered.
- Preserve the `N.)` number for life. Never renumber or reclaim a gap.
- Preserve the report title/body except for the lifecycle suffix and footer
  lifecycle line.
- Leave an empty Live Subject folder in place; deletion is separate work.
- Touch no unrelated report.

## Output

Report the original Live path, final Historical path, completion evidence,
contract outcomes or deferrals, and any unresolved limitation. Do not paste the
whole report unless asked.

## Boundaries

Do not create/update/reopen reports, choose a sent/read-specific terminal state,
infer completion from existence, overwrite a collision, renumber, remove the
dismissible footer, add workflow metadata at the top, send the report, or move a
file manually when evidence gates fail.

## Agent Provenance For Durable Artifacts

Finalization never replaces the original creator. Preserve the artifact's
`## Agent Provenance` section exactly, then append a new entry to its
`## Agent Change Log` naming the truthful acting agent, the finalization date,
the lifecycle action, and the status/path or content scope changed.

When same-stem Markdown, HTML, or PDF siblings exist, apply the same provenance
history to the complete artifact set. If a legacy artifact lacks reliable
creator evidence, record `Original writing agent: Not recorded` rather than
guessing, and log the current finalizer's work. Do not add embedded provenance
to product source, third-party files, databases, generated caches, skill
definitions, schema-sensitive or machine-consumed files, or other operational
files unless their schema explicitly supports it.

## Durable Artifact Format Handling

This skill still owns every evidence, footer, and reporting gate. Before
finalizing, discover same-stem `.md`, `.html`, and `.pdf` siblings and treat
them as one report artifact set. Preflight every destination, apply reported
content/status through the applicable format skill, rename the lifecycle suffix
on every sibling, and move the complete set together without changing the
permanent prefix or Topic.

HTML-only or PDF-only reports remain in that format; do not manufacture
Markdown. Stop rather than finalize only part of a sibling set. Extension-only
search and validation examples become format-neutral for this run.

## Validation

After finalization, confirm:

- the Live source no longer exists and Historical target exists
- filename ends `_reported.md`
- Subject and permanent `N.)` are unchanged and collision-free
- footer says REPORTED ✅ with created and reported dates
- exactly one canonical dismissible footer exists
- footer retains the delete-before-sending instruction and contains no mode tag
- report body is otherwise unchanged and UTF-8 is preserved

When updating this skill, run `quick_validate.py` with Python `-X utf8` and keep
stdout and stderr separate.
