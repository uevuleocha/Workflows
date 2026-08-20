# Global Skills Creator Auto Adoption Guide

This skill autonomously creates or syncs reusable agent skills from a local master skills folder to one or more global agent skill installs.

Every skill that writes Markdown tables — new or existing, into a durable artifact or into its own chat output — carries the portable Markdown table-alignment contract and a validation check so pipe alignment remains enforced after global installation. Skills that write no tables are exempt. Skills that create first-party durable artifacts also carry the durable-artifact provenance contract — a five-row agent provenance table (`Content owner`, `Original writing agent`, `Original writing LLM`, `Created`, `Artifact role`) immediately after each artifact's opening block, and an append-only five-column agent change log (`Date and Time | Agent | Model | Action | Scope`) as the last section. Skills whose artifacts carry a DEFINITION OF DONE additionally carry a Feedback Section for cross-agent messages, plus four canonical artifact-integrity rules: Checklist Tick Discipline; In-Pass And Deferred Real-World Verification; No Invented Sync Constraints; and Non-Blocking Wiki And Git Items. Immediately testable checks remain blocking, while genuinely later-use checks live in a separate non-blocking deferred checklist.

If you cloned this skill from someone else, do not assume the original maintainer's paths apply to your machine. Ask your agent to read this README and `SKILL.md`, then help you configure your own path stack before running autonomous create-and-sync work.

## Local Master Rule

By default, a machine should have one canonical local master skills folder. That folder is the source of truth for reusable skills before they are synced to global installs.

The local master can live in a dedicated skills workspace, such as `Workflows`, `John Skills`, or another personal workspace, or it can be a `skills/` folder inside an existing workspace. The exact location is the user's choice.

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
- Hermes: the Hermes desktop app's skills directory (on Windows, `%LOCALAPPDATA%\hermes\skills\`), under a `Personal/` category subfolder
- zCode: `~/.zcode/skills/`

These are candidates, not guarantees. The agent should verify each path exists before syncing.

## Depends On `global-sync`

This skill delegates its global-sync step to the `global-sync` skill (Mode A), so the same copy-and-validate workflow is used everywhere. **If you adopt this skill, adopt `global-sync` too.** If `global-sync` is unavailable at sync time, this skill pauses and tells you it is required; it only falls back to inline copy logic if you explicitly continue without it.
## Deterministic table dependency

Adopt `markdown-table-aligner` with this skill. It supplies the deterministic final padding pass for file-based Markdown tables; the portable rule remains the content and fallback contract.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.
