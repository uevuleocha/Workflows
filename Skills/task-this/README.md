# Task This — Adoption Guide

Creates and updates durable workspace housekeeping/admin task files as `Archive/Live/Tasks/…` artifacts. Every task depth requires Markdown action and verification checklists. Pending items use `[ ]`; items change to `[x]` only after user confirmation or recorded evidence, following the completed Uzzy SR Plan 20/21 checklist pattern.

## Dependency

`task-this` depends on the `prompt-contracts` skill. Every task it writes must embed a Prompt Contract (GOAL / CONSTRAINTS / FORMAT / DEFINITION OF DONE / FAILURE), authored by invoking `prompt-contracts` — see the `## Prompt Contract Integration (Mandatory)` section in `SKILL.md`. The contract's DEFINITION OF DONE clause is the task's single Definition of Done (there is no standalone `## Definition of Done` section). It runs with an availability guard and an inline fallback if `prompt-contracts` is not loaded.

**If you adopted `task-this` from Uzo (U-Z-O), also adopt `prompt-contracts` and `markdown-table-aligner`.** The aligner supplies the deterministic final padding pass for task tables; the portable rule remains the fallback contract. `finalize-task` also reads the embedded contract, so adopt it too for the full task lifecycle.

For the general mechanism, see the workspace's `Documentation/` folder, `3.) Skill-to-Skill Calls — Pattern and Registry.md`.

## Adoption Prompt

```text
Read this README and SKILL.md. This skill depends on `prompt-contracts` and `markdown-table-aligner`; make sure both are installed in
the same agent installs (Codex / Claude / Antigravity) as this skill. Use my OS path conventions and
ask before creating missing folders.
```

## Optional artifact formats

Pair with `html-this` or `pdf-this` for HTML-only or PDF-only human-readable artifacts while this skill retains content and workflow ownership.
