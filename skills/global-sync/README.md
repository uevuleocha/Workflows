# Global Sync Adoption Guide

This skill propagates an artifact that **already exists** in a local master skills folder out to one or more global agent skill installs (Codex, Claude, Antigravity, Hermes, zCode), validating every copy. It does not design or create artifacts — for that, use `global-skills-creator` (guided) or `global-skills-creator-auto` (autonomous).

If you cloned this skill from someone else, do not assume the original maintainer's paths apply to your machine. Ask your agent to read this README and `SKILL.md`, then help you configure your own path stack before running any sync.

## Local Master Rule

By default, a machine should have one canonical local master skills folder — the source of truth for reusable skills before they are synced to global installs. The local master can live in a dedicated skills workspace (such as `Uzzy Skills`) or a `skills/` folder inside an existing workspace. Once chosen, treat it as the default for that machine unless the user explicitly asks for a multi-master setup.

## Common Global Install Candidates

- Codex: `~/.codex/skills/`
- Claude: `~/.claude/skills/`
- Antigravity/Gemini: `~/.gemini/config/skills/`
- Hermes: the Hermes desktop app's skills directory (on Windows, `%LOCALAPPDATA%\hermes\skills\`), under a `Personal/` category subfolder
- zCode: `~/.zcode/skills/`

These are candidates, not guarantees. The agent should verify each path exists before syncing, and must never invent a missing path.

## Hermes Grouping

Hermes groups skills by category subfolder (each folder is a category in the Hermes desktop app). This skill syncs into a `Personal/` category and ensures a one-line `DESCRIPTION.md` exists for it. `Personal` is a sensible default anyone can keep; an adopter who prefers a different category name can tell the agent to use another.

## Depended On By

The following skills invoke `global-sync` (Mode A) as their mandatory global-sync step. If you adopt one of them, adopt `global-sync` too:

- `global-skills-creator`
- `global-skills-creator-auto`

If `global-sync` is unavailable when one of those skills reaches its sync step, that skill follows its availability guard: it pauses and tells you `global-sync` is required, and only falls back to inline copy logic if you explicitly continue without it. See the skill-to-skill call documentation in the workspace `Documentation/` folder for the full pattern.

## Adoption Prompt

Give this prompt to your agent:

```text
Read this README and the skill's SKILL.md. Help me configure the local master skills path and my global install paths (Codex, Claude, Antigravity, Hermes, zCode) for my machine. Use my OS conventions, do not assume the original maintainer's Windows paths, and ask before creating missing folders or using a Hermes category other than Personal.
```
