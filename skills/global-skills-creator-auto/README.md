# Global Skills Creator Auto Adoption Guide

This skill autonomously creates or syncs reusable agent skills from a local master skills folder to one or more global agent skill installs.

If you cloned this skill from someone else, do not assume the original maintainer's paths apply to your machine. Ask your agent to read this README and `SKILL.md`, then help you configure your own path stack before running autonomous create-and-sync work.

## Local Master Rule

By default, a machine should have one canonical local master skills folder. That folder is the source of truth for reusable skills before they are synced to global installs.

The local master can live in a dedicated skills workspace, such as `Uzzy Skills`, `John Skills`, or another personal workspace, or it can be a `skills/` folder inside an existing workspace. The exact location is the user's choice.

Once the user chooses a local master skills folder, the agent should treat it as the default rule for that user's machine. Do not create or use multiple local master folders unless the user explicitly asks for a multi-master setup.

## Adoption Prompt

Give this prompt to your agent:

```text
Read this README and the skill's SKILL.md. Help me configure the local master skills path and any global install paths for my machine. Use my OS conventions, do not assume the original maintainer's Windows paths, and ask before creating missing folders. Unless I explicitly ask for multiple local masters, help me choose one canonical local master skills folder and treat it as the default for this machine.
```

## Common Global Install Candidates

- Codex: `~/.codex/skills/`
- Claude: `~/.claude/skills/`
- Antigravity/Gemini: `~/.gemini/config/skills/`

These are candidates, not guarantees. The agent should verify each path exists before syncing.
