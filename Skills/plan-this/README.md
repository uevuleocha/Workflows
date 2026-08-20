# Plan This — Adoption Guide

Creates and updates durable, active implementation plans as `Archive/Live/Plans/…` artifacts. Every plan depth requires Markdown task and verification checklists. Pending items use `[ ]`; items change to `[x]` only after user confirmation or recorded evidence, following the completed Uzzy SR Plan 20/21 phase pattern.

Verification the executing agent can perform now remains in-pass and blocking. Checks that genuinely require later live use, elapsed time, user adoption, or an external event go in an optional `## Deferred Real-World Verification` checklist and never block finalization.

## Dependency

`plan-this` depends on the `prompt-contracts` skill. Every plan it writes must embed a Prompt Contract (GOAL / CONSTRAINTS / FORMAT / DEFINITION OF DONE / FAILURE), authored by invoking `prompt-contracts` — see the `## Prompt Contract Integration (Mandatory)` section in `SKILL.md`. It runs with an availability guard and an inline fallback if `prompt-contracts` is not loaded.

**If you adopted `plan-this` from Uzo (U-Z-O), also adopt `prompt-contracts` and `markdown-table-aligner`.** The aligner supplies the deterministic final padding pass for plan tables; the portable rule remains the fallback contract. `finalize-plan` also reads the embedded contract, so adopt it too for the full plan lifecycle.

For the general mechanism, see the workspace's `Documentation/` folder, `3.) Skill-to-Skill Calls — Pattern and Registry.md`.

## Adoption Prompt

```text
Read this README and SKILL.md. This skill depends on `prompt-contracts` and `markdown-table-aligner`; make sure both are installed in
the same agent installs (Codex / Claude / Antigravity) as this skill. Use my OS path conventions and
ask before creating missing folders.
```

## Optional artifact formats

Pair with `html-this` or `pdf-this` for HTML-only or PDF-only human-readable artifacts while this skill retains content and workflow ownership.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.
