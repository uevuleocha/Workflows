# Agent Instructions - {Workspace Name}

`CLAUDE.md` is the canonical project contract for this workspace.

At the start of every conversation in this project workspace, before any substantive reply, read `CLAUDE.md` from the workspace root and treat it as the source of truth. This applies even if the first user message is only a greeting or general check-in.

This file is an agent wrapper for Codex, Antigravity, Hermes, and zCode compatibility. Do not duplicate the full operating contract here; use `CLAUDE.md` for canonical safety rules, skills workflow, active-plan handling, workspace layout, communication style, and mode behavior.

Codex owns the root `.codex/` directory. Do not modify its harness-managed `config.toml` unless the user explicitly requests Codex workspace settings changes. Other manually maintained coordination settings belong under `.agents/`.

If instructions conflict, prefer the most recent direct user instruction, then `CLAUDE.md`, then this wrapper.

## [CODEX ONLY Instruction] - Antigravity (All Antigravity Models) && Claude (All Claude Models) && Hermes (All Hermes Models) && zCode (All zCode Models), ignore this entire section!

After reading `CLAUDE.md`, also read `.codex/settings.local.json` if it exists. Treat it as workspace-local Codex coordination settings. It does not replace Codex app-managed permissions, global config, or the canonical project contract in `CLAUDE.md`.

## [ANTIGRAVITY ONLY Instruction] - Codex (All Codex Models) && Claude (All Claude Models) && Hermes (All Hermes Models) && zCode (All zCode Models), ignore this entire section!

After reading `CLAUDE.md`, also read `.agents/.antigravity/settings.local.json` if it exists. Treat it as workspace-local Antigravity coordination settings.

## [HERMES ONLY Instruction] - Codex (All Codex Models) && Claude (All Claude Models) && Antigravity (All Antigravity Models) && zCode (All zCode Models), ignore this entire section!

After reading `CLAUDE.md`, also read `.agents/.hermes/settings.local.json` if it exists. Treat it as workspace-local Hermes coordination settings. It does not replace Hermes app-managed permissions, global config, or the canonical project contract in `CLAUDE.md`.

## [ZCODE ONLY Instruction] - Codex (All Codex Models) && Claude (All Claude Models) && Antigravity (All Antigravity Models) && Hermes (All Hermes Models), ignore this entire section!

After reading `CLAUDE.md`, also read `.agents/.zcode/settings.local.json` if it exists. Treat it as workspace-local zCode coordination settings. It does not replace zCode app-managed permissions, global config, or the canonical project contract in `CLAUDE.md`.
