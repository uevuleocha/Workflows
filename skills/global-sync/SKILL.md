---
name: global-sync
description: Propagate an existing local-master artifact (skills now; agents/sub-agents as a future stub mode) out to the configured global install locations (Codex, Claude, Antigravity, Hermes, zCode), validating every copy. Use when the user explicitly invokes /global-sync, use global-sync, "sync this skill globally", "sync all skills", "re-sync after an update", "push this skill to Codex/Claude/Antigravity/Hermes/zCode", or clear equivalents asking to propagate something that already exists locally — not to design or create a new one.
---

# Global Sync

Propagate an artifact that **already exists** in the local master out to the configured global install locations, then validate every copy. This is the single, repeatable sync workflow for the whole ecosystem: standalone when the user updates a skill by hand, and as the mandatory sync step called by `global-skills-creator` and `global-skills-creator-auto`.

This skill does not design or create artifacts. If the named artifact does not exist in the local master, stop and point the user to `global-skills-creator` (guided) or `global-skills-creator-auto` (autonomous) instead.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## UTF-8 Rule

Always use UTF-8 for every skill, workflow, markdown, YAML, and helper script copied or validated through this skill. When validating, run Python in UTF-8 mode with `-X utf8`. Preserve UTF-8 content across every target copy.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/global-sync`
- `use global-sync`
- `use the global-sync skill`
- `sync this skill globally`
- `sync all skills`
- `re-sync after an update`
- `push this skill to Codex, Claude, Antigravity, Hermes, and zCode`
- clear equivalents asking to propagate an existing local-master artifact to the global installs

## Modes

- **Mode A — Skills (fully built).** Propagate a folder-style skill (or all skills) from the local master `skills/` folder to each global skills target.
- **Mode B — Agents / Sub-agents (stub, not implemented).** Reserved for propagating custom sub-agents once the user starts saving them. See the Mode B section.

Pick the mode from context. Default to Mode A unless the user clearly names an agent/sub-agent artifact.

## Default Path Stack (Mode A)

Resolve these before copying. On Uzo's machine the maintainer defaults are:

```text
Local master:
C:\Users\Admin\Uzzys Universe\MilkyWay\Tools\Workflows\skills\<skill>\

Codex global:
C:\Users\Admin\.codex\skills\<skill>\

Claude global:
C:\Users\Admin\.claude\skills\<skill>\

Antigravity global:
C:\Users\Admin\.gemini\config\skills\<skill>\

Hermes global:
C:\Users\Admin\AppData\Local\hermes\skills\Personal\<skill>\

zCode global:
C:\Users\Admin\.zcode\skills\<skill>\
```

These are known-good defaults for Uzo's machine, not universal paths. On any other machine, resolve the user's own `~/.codex/skills/`, `~/.claude/skills/`, `~/.gemini/config/skills/`, Hermes app-data skills directory, and `~/.zcode/skills/`, and translate examples into the host OS path style. Never invent a path — if a target base directory is missing, stop and ask the user for the replacement path for that specific target.

## Hermes Specifics (Mode A)

Hermes groups skills by **category subfolder** (each folder becomes a category in the Hermes desktop app), unlike the flat Codex/Claude/Antigravity targets. Synced skills go under a `Personal/` category:

```text
C:\Users\Admin\AppData\Local\hermes\skills\Personal\<skill>\
```

`Personal` is the default grouping used in this skill and its README. An adopter who already has a `Personal/` folder, or who prefers a different category, can tell the agent to use another name — but `Personal` is a sensible default anyone can keep.

Ensure a category `DESCRIPTION.md` exists at `...\hermes\skills\Personal\DESCRIPTION.md`, matching Hermes' one-line frontmatter convention. If it is missing, create it:

```yaml
---
description: Personal reusable skills synced from the Workflows local master. Cross-agent workflow skills authored for use across Claude, Codex, Antigravity, and Hermes.
---
```

## Mode A Workflow

1. **Resolve scope.** A named skill, a comma-separated list of skills, or `all` (every folder under the local master `skills/`).
2. **Confirm each named skill exists in the local master.** If a named skill is missing locally, stop and report it — this skill never creates artifacts.
3. **Validate the local master first.** Run `quick_validate.py` (UTF-8 mode) on each in-scope local master skill. If any fails, stop and report — never propagate a broken skill to the global targets.
4. **Verify target base directories.** For each of Codex, Claude, Antigravity, Hermes, and zCode, confirm the global skills base directory exists. If one is missing, stop and ask for the replacement path for that target (do not guess).
5. **Copy per target.** For each in-scope skill × each target: create the destination skill folder if missing (Hermes → under `Personal/`; zCode → flat under `~/.zcode/skills/`), then true-copy with `Copy-Item -Recurse -Force` (not `Write` — a real copy preserves content faithfully) of `SKILL.md`, `agents/openai.yaml`, and any `scripts/`, `references/`, or `assets/` present.
6. **Ensure Hermes category file.** Confirm or create `...\hermes\skills\Personal\DESCRIPTION.md`.
7. **Validate every copy.** Run `quick_validate.py` (UTF-8 mode) against each synced copy at each target.
8. **Report.** A skill × target × validation-result table, plus any replacement paths used and any targets skipped (with the reason).

## Mode B — Agents / Sub-agents (STUB, not implemented)

Not built yet. Reserved for the day the user starts saving custom sub-agents and wants their propagation automated. What is already confirmed, to save future work:

- Claude Code custom sub-agents are **single Markdown files** with YAML frontmatter (`name`, `description`, `tools`, optionally `model`), living at `.claude/agents/<name>.md` (project-level, discovered by walking up to the repo root) or `~/.claude/agents/<name>.md` (user-global). This is a **single-file** shape, not a folder — so Mode A's folder-copy logic does not apply as-is.
- Codex, Antigravity, Hermes, and zCode sub-agent conventions are **not yet confirmed**. Codex's `AGENTS.md` is a single contract/wrapper file, **not** a registry of individually named sub-agents — do not assume equivalence.

**Before building Mode B:** confirm each platform's real sub-agent mechanism (if any), decide the target path stack for single-file agents, then mirror Mode A's shape — resolve path stack → validate local → copy → validate targets — adapted for single-file artifacts. Until then, if a user asks to sync an agent, explain that Mode B is a stub and stop.

## Safety Rules

- **Additive / overwrite only.** Write new and changed files into each target. Never delete a skill from a global target just because it is absent from the local master — pruning is a separate, explicitly requested action, never done here.
- **Never invent a missing directory.** If a target base directory does not exist, stop and ask for the replacement path for that specific target.
- **Never claim success without validation.** Only report a target as synced after the copied files exist and `quick_validate.py` has run against them.
- **True copy, not rewrite.** Use `Copy-Item -Recurse -Force`, not `Write`, so content is preserved faithfully.
- **Local-master-broken means stop.** A skill that fails local validation is never propagated.

## Validation

After a run:

- Confirm each in-scope local master skill passed `quick_validate.py` before any copy.
- Confirm each synced copy exists at each target and passed `quick_validate.py`.
- Confirm the Hermes `Personal/DESCRIPTION.md` exists.
- Report the full skill × target × result table, replacement paths used (or `none`), and any manual UI checks still needed.

When creating or updating this skill itself, validate the folder-style skill with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
