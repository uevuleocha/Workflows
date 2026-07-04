---
name: global-skills-creator-auto
description: Autonomously create reusable skills from a local master and sync them across Codex, Claude, and Antigravity global skill or workflow locations, using reasonable defaults first so the user can refine afterward. Use when the user explicitly asks for automatic skill creation, autonomous skill generation, fast create-and-sync behavior, or "use global-skills-creator-auto".
---

# Global Skills Creator Auto

Autonomously create a reusable skill from a local master skills folder, then optionally promote it to configured global locations for Codex, Claude, and Antigravity. On Uzo's machine, the default local master is the Uzzy Skills workspace. On any other machine, first discover or ask for the user's local master skills folder and global skill install paths.

This is the automatic variant of `global-skills-creator`. Use it when the user wants the agent to infer sensible defaults, create the skill, sync it globally, validate it, and then allow refinement afterward.

Use `session-summary/SKILL.md` from the resolved local master skills folder only as a structural muse when it exists: clear frontmatter, concise sections, required-input prompts, safety notes, and validation discipline. Do not copy the `session-summary` workflow unless the new skill actually summarizes sessions.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## UTF-8 Rule

Always use UTF-8 for every skill, workflow, markdown, YAML, and helper script created or edited through this skill.

When writing or reading text from scripts, specify UTF-8 explicitly, for example `encoding="utf-8"` in Python. Do not rely on Windows default encoding.

When validating skills, always run Python in UTF-8 mode with `-X utf8`.

When syncing global copies, preserve UTF-8 content across the local master, Codex global, Claude global, and Antigravity global.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/global-skills-creator`
- `/global-skills-creator-auto`
- `use the global-skills-creator skill`
- `use the global-skills-creator-auto skill`
- `automatic global skill creation`
- `autonomous skill creation`
- `auto-create a skill`
- `create a global skill`
- `make a skill for all agents`
- `sync this skill to Codex, Claude, and Antigravity`
- clear equivalents where the user asks for a reusable skill and cross-agent promotion

If the user invokes the non-auto `global-skills-creator`, use the guided/default workflow instead. This auto variant is specifically for cases where the user wants fast create-and-sync behavior and expects to refine afterward.

If the user only wants a quick idea or draft, do not create files until they approve skill creation.

## Required Inputs

Before writing files, the agent needs to know or infer these inputs. Use reasonable defaults where possible. Only present this template to the user when critical information is genuinely missing and cannot be inferred:

```text
We need to define the new skill before writing it.

1. Skill Name: hyphen-case name for the skill (e.g., "initialize", "debug", "session-summary").
2. Purpose: (What should this skill do? e.g., initialize a new session, set up the workspace, onboard the agent at the start of a conversation?)
3. Trigger Phrases: The commands or phrases that invoke this skill (e.g., /initialize, use initialize).
4. Required Inputs: What the agent needs from the user or workspace before it can run.
5. Outputs: What the skill produces — templates, reports, loaded context, files, etc.
6. Reference Files: Existing skills, workflows, summaries, or files the skill should read as context.
7. Resources Needed (scripts/references/assets/none): Whether the skill folder needs extra subfolders beyond SKILL.md and agents/.
8. Validation Needed: Any checks beyond the standard sync validation — e.g., smoke-test phrases, custom validators, or "none" if standard folder/frontmatter validation is sufficient.
9. Create local + Codex + Claude + Antigravity copies?: Whether to sync the skill to all 4 locations or keep it local-only.
```

If the user has already provided enough detail, proceed with the reasonable defaults and record them in the final status.

## Default Path Stack

Resolve the path stack before creating or syncing. The user should normally have **one canonical local master skills folder per machine** unless they explicitly ask for multiple local masters. Help the user choose that folder when needed, and after it is chosen, treat it as the rule for that user's machine for future skill creation and sync work.

Preferred discovery order:

1. If the host workspace contains a `skills/` folder and a canonical contract file such as `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`, treat `<project root>/skills/` as the local master candidate.
2. If no local master candidate is obvious, ask the user whether they want a local master folder, where it should live, and whether it should be the machine's single canonical local master.
3. Resolve global install candidates from the user's home directory:
   - Codex: `~/.codex/skills/`
   - Claude: `~/.claude/skills/`
   - Antigravity/Gemini: `~/.gemini/config/skills/`
4. If a target does not exist, stop and ask whether to create it, skip it, or use a different path.

Do not assume Windows paths on macOS or Linux. Translate examples into the host OS path style.

Maintainer defaults for Uzo's machine:

```text
Local master:
C:\Users\Admin\Uzzys Universe\Galaxies\Tools\Uzzy Skills\skills\[Skill-name]\SKILL.md

Codex global:
C:\Users\Admin\.codex\skills\[Skill-name]\SKILL.md

Claude global:
C:\Users\Admin\.claude\skills\[Skill-name]\SKILL.md

Antigravity global:
C:\Users\Admin\.gemini\config\skills\[Skill-name]\SKILL.md
```

These maintainer defaults are known-good examples for Uzo's machine, not universal paths.

Create or update the local master first. After the local master is complete, sync it to Codex, Claude, and Antigravity as folder-style skill copies.

## Path Handling

Before creating or syncing, verify each resolved base directory exists:

- Local master skills folder
- Codex global skills folder
- Claude global skills folder
- Antigravity/Gemini global skills folder

If any directory is missing, stop and ask the user for the replacement path for that specific target.

Use this wording:

```text
I could not find your [target] directory. What [target] directory should I use?

Example:
`[example path]`
```

Do not guess alternative global paths silently. If the user provides a replacement path, use it for that run and record it in the final status. If the user confirms a canonical local master skills folder, state that it should remain the default local master for that machine unless the user explicitly chooses a different multi-master setup.

## Creation Workflow

1. Read the requested references, including existing skills or summaries the user named.
2. Normalize the skill name to lowercase hyphen-case and confirm it has only lowercase letters, digits, and hyphens.
3. Decide whether the skill needs only `SKILL.md` and `agents/openai.yaml`, or also `scripts/`, `references/`, or `assets/`.
4. Create the skill folder under the resolved local master skills folder.
5. Write `SKILL.md` with only `name` and `description` in frontmatter.
6. Write `agents/openai.yaml` for Codex UI metadata.
7. Validate the local master.
8. Sync to global locations after local validation passes.
9. Validate the folder-style global copies (including Antigravity).
10. Report files created, validations run, replacement directories used, and any pending manual UI checks.

Ecosystem consistency rule: every folder-style skill must include `agents/openai.yaml` in the local master, Codex global copy, and Claude global copy. Claude may not require this file today, but the folder structure must remain mirrored unless the user later decides to remove `agents/` from all Claude global skills at once.

Prefer the official Codex `skill-creator` scripts when available. If Python or the scripts are unavailable, create the minimal folder structure manually and explain which validation could not run.

## Permission Behavior

If the user invokes this skill and approves creating a skill, treat that as approval to create:

- the local master copy
- the Codex global copy
- the Claude global copy
- the Antigravity global skill copy

Codex and Claude must still follow their runtime permission model. If writing outside the workspace requires elevated approval, request it.

Antigravity must still follow the 2FA edit rule from `AGENTS.md` before creating or editing files:

```text
"make the edit" | "greenlight" | "approved" | "execute plan" | "go ahead" | "apply changes" | "do it" | "push to drive"
```

## Sync Rules

For Codex global:

- Create `[resolved Codex global skills folder]\[Skill-name]\`.
- Copy `SKILL.md`.
- Copy `agents\openai.yaml`.
- Copy any required `scripts/`, `references/`, or `assets/`.

For Claude global:

- Create `[resolved Claude global skills folder]\[Skill-name]\`.
- Copy `SKILL.md`.
- Copy `agents\openai.yaml` as a required mirror file.
- Copy any required resources.
- Keep the Claude folder-style skill structure mirrored with the local master and Codex global copy unless the user later decides to remove `agents/` from all Claude global skills at once.

For Antigravity:

- Create `[resolved Antigravity/Gemini global skills folder]\[Skill-name]\`.
- Copy `SKILL.md`.
- Copy `agents\openai.yaml` as a required mirror file.
- Copy any required resources.
- Keep the Antigravity folder-style skill structure mirrored.

## Validation Rules

Always validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).

Run this validator for:

- local master folder
- Codex global folder
- Claude global folder, if it is folder-style and contains `SKILL.md`
- Antigravity global folder

If validation fails, read the error, fix the skill, and rerun validation.

## Skill Writing Guidelines

Keep the skill focused on the reusable procedure another agent needs. Do not add extra documentation files such as README, changelog, or install guides unless the user explicitly asks.

Do:

- keep `SKILL.md` concise and procedural
- include all trigger logic in the `description`
- use required-input prompts for missing user intent
- use references only when they reduce context bloat
- use deterministic scripts when repeated fragile work needs reliability
- use UTF-8 for all markdown, YAML, workflow, and script text
- report validation outcomes clearly

Do not:

- invent paths when a directory is missing
- rely on Windows default encoding for text files
- claim global sync happened before verifying files exist
- claim validation passed unless the validator or manual check actually ran
- copy another skill's task-specific workflow when it is only a style reference

## Final Status Format

After creating or updating a skill, report:

- local master path
- Codex global path
- Claude global path
- Antigravity skill path
- validations run and results
- replacement directories supplied by the user, or `none`
- manual UI checks still needed, if any
