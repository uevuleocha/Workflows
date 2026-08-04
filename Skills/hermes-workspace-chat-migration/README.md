# Hermes Workspace Chat Migration — Adoption Guide

Migrates Hermes Desktop chat sessions between workspaces (single SQLite layer: `state.db.sessions.{cwd, git_repo_root}`), with backups, one-session testing, manifests, and verification.

Hermes is the simplest migration model of the platforms that have migration skills. There are no transcript files to relocate (messages live in `state.db.messages` — never touched), no global-state JSON, no protobuf blobs, no separate sidebar index database, and no sidecar folders. The entire migration is a two-column `UPDATE` on the `sessions` table: `cwd` (grouping signal + resume working directory) and `git_repo_root` (auto-project fallback grouping).

## Dependency

`hermes-workspace-chat-migration` depends on the `session-summary` skill. Both the Front-Door and Execution workflows close by producing an explicit handoff/report summary through `session-summary` — not hand-written prose (see the `## Session Summary Integration` section in `SKILL.md`). It runs with an availability guard and falls back to a plain markdown summary if `session-summary` is not loaded.

**If you adopted `hermes-workspace-chat-migration` from Uzo (U-Z-O), also adopt `session-summary`.** This skill also ships its own bundled `scripts/` — keep those with it when you copy the skill.

For the general mechanism, see the workspace's `Documentation/` folder, `3.) Skill-to-Skill Calls — Pattern and Registry.md`.

## Adoption Prompt

```text
Read this README and SKILL.md. This skill depends on `session-summary` and ships its own scripts/ folder; make sure `session-summary` is installed in the same agent installs (Codex / Claude / Antigravity / Hermes / zCode) and that the scripts travel with the skill. Use my OS path conventions and ask before creating missing folders.
```

## Optional artifact formats

Pair with `html-this` or `pdf-this` for HTML-only or PDF-only manifests, handoffs, and reports while this skill retains migration ownership.
