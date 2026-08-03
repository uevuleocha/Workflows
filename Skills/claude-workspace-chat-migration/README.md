# Claude Workspace Chat Migration — Adoption Guide

Migrates Claude Desktop local chat sessions between workspaces (transcript JSONL grouping + Desktop
chat store), with backups, one-session testing, manifests, and verification.

## Dependency

`claude-workspace-chat-migration` depends on the `session-summary` skill. Both the Front-Door and
Execution workflows close by producing an explicit handoff/report summary through `session-summary`
— not hand-written prose (see the `## Session Summary Integration` section in `SKILL.md`). It runs
with an availability guard and falls back to a plain markdown summary if `session-summary` is not
loaded.

**If you adopted `claude-workspace-chat-migration` from Uzo (U-Z-O), also adopt `session-summary`.**
This skill also ships its own bundled `scripts/` — keep those with it when you copy the skill.

For the general mechanism, see the workspace's `Documentation/` folder,
`3.) Skill-to-Skill Calls — Pattern and Registry.md`.

## Adoption Prompt

```text
Read this README and SKILL.md. This skill depends on `session-summary` and ships its own scripts/
folder; make sure `session-summary` is installed in the same agent installs (Codex / Claude /
Antigravity) and that the scripts travel with the skill. Use my OS path conventions and ask before
creating missing folders.
```

## Optional artifact formats

Pair with `html-this` or `pdf-this` for HTML-only or PDF-only manifests,
handoffs, and reports while this skill retains migration ownership.
