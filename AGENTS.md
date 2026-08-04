# Agent Instructions - Workflows

`CLAUDE.md` is the canonical project contract for this workspace.

For LLM wiki setup, sync, query, or lint work, read and obey `wiki/wiki-schema.md`.

At the start of every conversation in this project workspace, before any substantive reply, read `CLAUDE.md` from the workspace root and treat it as the source of truth. This applies even if the first user message is only a greeting or general check-in.

This file is an agent compatibility wrapper for Codex, Antigravity, Hermes, and Z Code. Do not duplicate the full operating contract here; use `CLAUDE.md` for canonical safety rules, skills workflow, active-plan handling, workspace layout, communication style, and mode behavior.

Claude is governed directly by `CLAUDE.md`. Codex owns the root `.codex/` directory, including harness-managed `config.toml` and workspace-local `settings.local.json`. Other manually maintained coordination settings live under `.agents/`.

If instructions conflict, prefer the most recent direct user instruction, then `CLAUDE.md`, then this wrapper.

## [CODEX ONLY Instruction] - Antigravity (All Antigravity Models) && Claude (All Claude Models) && Hermes (All Hermes Models) && Z Code (All Z Code Models), ignore this entire section!

After reading `CLAUDE.md`, also read `.codex/settings.local.json` if it exists. Treat it as workspace-local Codex coordination settings. Do not modify `.codex/config.toml` unless the user explicitly asks to change Codex workspace settings. These files do not replace Codex app-managed permissions, global config, or the canonical project contract in `CLAUDE.md`.

## [ANTIGRAVITY ONLY Instruction] - Codex (All Codex Models) && Claude (All Claude Models) && Hermes (All Hermes Models) && Z Code (All Z Code Models), ignore this entire section!

After reading `CLAUDE.md`, also read `.agents/.antigravity/settings.local.json` if it exists. Treat it as workspace-local Antigravity coordination settings. It does not replace the DeepMind Agentic Framework Sandbox or the canonical project contract in `CLAUDE.md`.

## [HERMES ONLY Instruction] - Codex (All Codex Models) && Claude (All Claude Models) && Antigravity (All Antigravity Models) && Z Code (All Z Code Models), ignore this entire section!

After reading `CLAUDE.md`, also read `.agents/.hermes/settings.local.json` if it exists. Treat it as workspace-local Hermes coordination settings. It does not replace Hermes app-managed permissions, global config, or the canonical project contract in `CLAUDE.md`.

## [Z CODE ONLY Instruction] - Codex (All Codex Models) && Claude (All Claude Models) && Antigravity (All Antigravity Models) && Hermes (All Hermes Models), ignore this entire section!

After reading `CLAUDE.md`, also read `.agents/.zcode/settings.local.json` if it exists. Treat it as workspace-local Z Code coordination settings. It does not replace Z Code app-managed permissions, global config, or the canonical project contract in `CLAUDE.md`.
