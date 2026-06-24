---
name: global-skills-creator
description: Guided creation of reusable skills from a local master, with user questions, prompt/style collection, a proposed design checkpoint, and then optional sync across Codex, Claude, and Antigravity global skill or workflow locations. Use when the user asks to create, design, promote, validate, or globally install a reusable skill and should be consulted before files are written.
---

# Global Skills Creator

Create a reusable skill, starting from the local master copy under the configured Uzzy Skills workspace (`C:\Users\Admin\Uzzys Universe\Galaxies\Tools\Uzzy Skills\skills\` by default), then promote it to the configured global locations for Codex, Claude, and Antigravity.

This is the guided/default variant. It must collect the user's prompt, draft, style notes, and design preferences before writing skill files. For autonomous create-and-sync behavior, use `global-skills-creator-auto`.

Use `C:\Users\Admin\Uzzys Universe\Galaxies\Tools\Uzzy Skills\skills\session-summary\SKILL.md` only as a structural muse: clear frontmatter, concise sections, required-input prompts, safety notes, and validation discipline. Do not copy the `session-summary` workflow unless the new skill actually summarizes sessions.

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
- `use the global-skills-creator skill`
- `create a global skill`
- `make a skill for all agents`
- `sync this skill to Codex, Claude, and Antigravity`
- clear equivalents where the user asks for a reusable skill and cross-agent promotion

If the user only wants a quick idea or draft, do not create files until they approve skill creation.

If the user explicitly wants the agent to infer the design and create/sync quickly without the guided question stage, use `global-skills-creator-auto` instead.

## Guided Design Rule

Before writing, creating, editing, or syncing any skill files, always stop for user input. This applies even when the user says something like `create a debug skill`.

First, ask for the user's own prompt, draft, style notes, or desired shape for the skill:

```text
Please enter any prompt, draft, style notes, required sections, trigger phrases, examples, constraints, or safety rules you had in mind for this skill.
```

Then collect or confirm the required inputs using the template in the `Required Inputs` section below. If the user already provided some of them, summarize what is known and ask only for the missing or uncertain parts.

Once all inputs are collected, present them back as a proposed skill design checkpoint — including any assumptions being made — and ask for explicit approval before creating or editing files. Use this wording:

```text
Please confirm before I create or edit any skill files. You can say `approve`, `make the edit`, `go ahead`, or give revisions.
```

Do not treat silence, vague enthusiasm, or an initial skill request as approval to write files.

## Required Inputs

Before writing files, make sure these are known. When information is missing, present the explanatory key first, then the compact copy-paste-fill template for the user to return.

Use this exact response shape:

```text
We need to define the new skill before writing it.

Skill Creation Intake Key

1. Skill Name: hyphen-case name for the skill (e.g., "initialize", "debug", "session-summary").
2. Purpose: What should this skill do? For example, initialize a new session, set up the workspace, onboard the agent, inspect code, summarize context, or run a repeatable workflow.
3. Trigger Phrases: The commands or phrases that invoke this skill (e.g., /initialize, use initialize, use the debug skill).
4. Required Inputs: What the agent needs from the user or workspace before it can run, such as file paths, plan names, mode choice, project name, or approval wording.
5. Outputs: What the skill produces, such as templates, reports, loaded context, files, exact code blocks, validation results, or synced skill folders.
6. Reference Files: Existing skills, workflows, summaries, plans, documentation, or source files the skill should read as context.
7. Resources Needed: Whether the skill folder needs extra subfolders beyond SKILL.md and agents/, such as scripts/, references/, assets/, or none.
8. Validation Needed: Any checks beyond standard folder/frontmatter validation, such as smoke-test phrases, custom validators, render checks, sync parity checks, or none.
9. Create local + Codex + Claude + Antigravity copies?: Whether to sync the skill to all 4 locations or keep it local-only.

Skill Creation Intake

1. Skill Name =
2. Purpose =
3. Trigger Phrases =
4. Required Inputs =
5. Outputs =
6. Reference Files =
7. Resources Needed (scripts/references/assets/none) =
8. Validation Needed =
9. Create local + Codex + Claude + Antigravity copies? =
```

If the user has already provided enough detail, do not proceed directly to file creation. First present the proposed skill design checkpoint from `Guided Design Rule` and wait for explicit approval or revisions.

## Default Path Stack

Use these as the default/example paths:

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

The global skill paths above are literal — they are real install locations on the user's machine. The local master path points to the dedicated Uzzy Skills workspace inside this Universe.

Create or update the local master first. After the local master is complete, sync it to Codex, Claude, and Antigravity as folder-style skill copies.

## Path Handling

Before creating or syncing, verify each base directory exists:

- Local skills folder: `C:\Users\Admin\Uzzys Universe\Galaxies\Tools\Uzzy Skills\skills\`
- Codex global skills folder: `C:\Users\Admin\.codex\skills\`
- Claude global skills folder: `C:\Users\Admin\.claude\skills\`
- Antigravity global skills folder: `C:\Users\Admin\.gemini\config\skills\`

If any directory is missing, stop and ask the user for the replacement path for that specific target.

Use this wording:

```text
I could not find your [target] directory. What [target] directory should I use?

Example:
`[example path]`
```

Do not guess alternative global paths silently. If the user provides a replacement path, use it for that run and record it in the final status.

## Creation Workflow

1. Read the requested references, including existing skills or summaries the user named.
2. Normalize the skill name to lowercase hyphen-case and confirm it has only lowercase letters, digits, and hyphens.
3. Decide whether the skill needs only `SKILL.md` and `agents/openai.yaml`, or also `scripts/`, `references/`, or `assets/`.
4. Create the local master folder under `C:\Users\Admin\Uzzys Universe\Galaxies\Tools\Uzzy Skills\skills\[Skill-name]\`.
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

- Create `C:\Users\Admin\.codex\skills\[Skill-name]\`.
- Copy `SKILL.md`.
- Copy `agents\openai.yaml`.
- Copy any required `scripts/`, `references/`, or `assets/`.

For Claude global:

- Create `C:\Users\Admin\.claude\skills\[Skill-name]\`.
- Copy `SKILL.md`.
- Copy `agents\openai.yaml` as a required mirror file.
- Copy any required resources.
- Keep the Claude folder-style skill structure mirrored with the local master and Codex global copy unless the user later decides to remove `agents/` from all Claude global skills at once.

For Antigravity:

- Create `C:\Users\Admin\.gemini\config\skills\[Skill-name]\`.
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
