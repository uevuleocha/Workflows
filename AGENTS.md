# Agent Instructions - Uzzys World

`CLAUDE.md` is the canonical project contract for this workspace.

At the start of every conversation in this project workspace, before any substantive reply, read `CLAUDE.md` from the workspace root and treat it as the source of truth. This applies even if the first user message is only a greeting or general check-in.

This file is only an agent wrapper for Codex and Antigravity compatibility. Do not duplicate the full operating contract here; use `CLAUDE.md` for canonical safety rules, skills workflow, active-plan handling, workspace layout, communication style, and mode behavior.

If instructions conflict, prefer the most recent direct user instruction, then `CLAUDE.md`, then this wrapper.

## [CODEX ONLY Instruction] - Antigravity (All Antigravity Models) && Claude (All Claude Models), ignore this entire section!

After reading `CLAUDE.md`, also read `.codex/settings.local.json` if it exists. Treat it as workspace-local Codex coordination settings. It does not replace Codex app-managed permissions, global config, or the canonical project contract in `CLAUDE.md`.

## [ANTIGRAVITY ONLY Instruction] - Codex (All Codex Models) && Claude (All Claude Models), ignore this entire section!

After reading `CLAUDE.md`, also read `.antigravity/settings.local.json` if it exists. Treat it as workspace-local Antigravity coordination settings.