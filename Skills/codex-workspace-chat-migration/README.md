# Codex Workspace Chat Migration — Adoption Guide

Migrates Codex Desktop chat sessions between workspaces (session JSONL metadata, global-state workspace hints, and the `state_5.sqlite` threads), with backups, one-session testing, manifests, and verification.

## Dependency

`codex-workspace-chat-migration` depends on the `session-summary` skill. Both the Front-Door and Execution workflows close by producing an explicit handoff/feedback summary through `session-summary` — not hand-written prose (see the `## Session Summary Integration` section in `SKILL.md`). It runs with an availability guard and falls back to a plain markdown summary if `session-summary` is not loaded.

**If you adopted `codex-workspace-chat-migration` from Uzo (U-Z-O), also adopt `session-summary`.** This skill also ships its own bundled `scripts/` — keep those with it when you copy the skill.

For the general mechanism, see the workspace's `Documentation/` folder, `3.) Skill-to-Skill Calls — Pattern and Registry.md`.

## Adoption Prompt

```text
Read this README and SKILL.md. This skill depends on `session-summary` and ships its own scripts/
folder; make sure `session-summary` is installed in the same agent installs (Codex / Claude /
Antigravity) and that the scripts travel with the skill. Use my OS path conventions and ask before
creating missing folders.
```

## Optional artifact formats

Pair with `html-this` or `pdf-this` for HTML-only or PDF-only manifests, handoffs, and feedback summaries while this skill retains migration ownership.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.
