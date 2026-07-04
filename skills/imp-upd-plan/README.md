# Imp Upd Plan — Adoption Guide

Creates and updates durable, active implementation plans as `Archive/Plans/…` artifacts.

## Dependency

`imp-upd-plan` depends on the `prompt-contracts` skill. Every plan it writes must embed a Prompt
Contract (GOAL / CONSTRAINTS / FORMAT / DEFINITION OF DONE / FAILURE), authored by invoking
`prompt-contracts` — see the `## Prompt Contract Integration (Mandatory)` section in `SKILL.md`. It
runs with an availability guard and an inline fallback if `prompt-contracts` is not loaded.

**If you adopted `imp-upd-plan` from Uzo (U-Z-O), also adopt `prompt-contracts`.** Without it, every
plan falls back to an inline contract and you lose the dedicated contract-authoring and
self-verification quality. `finalize-plan` also reads that embedded contract, so adopt it too for the
full plan lifecycle.

For the general mechanism, see the workspace's `Documentation/` folder,
`3.) Skill-to-Skill Calls — Pattern and Registry.md`.

## Adoption Prompt

```text
Read this README and SKILL.md. This skill depends on `prompt-contracts`; make sure it is installed in
the same agent installs (Codex / Claude / Antigravity) as this skill. Use my OS path conventions and
ask before creating missing folders.
```
