---
name: initialize
description: Initialize a new chat session by reading the workspace blueprint and presenting the "Tell Me More Boss!" structured intake template. Use when the user explicitly invokes /initialize, use initialize, use the initialize skill, or a clear equivalent naming this skill.
---

# Initialize

Initialize a new chat session by onboarding the agent and presenting a structured intake template for the user to fill.

This skill reads the workspace blueprint, presents the **"Tell Me More Boss!"** template, and waits for the user to fill and return it. After receiving the filled template, the agent loads the specified files, follows the user's instructions, and enters the requested mode. This is a one-shot intake tool, not a persistent mode.

## Project Contract

This skill operates under the project's canonical contract for the active agent platform (for example, `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

For Claude, do not read `AGENTS.md` by default unless the user, the platform, or another loaded project instruction explicitly points Claude to that file. Treat `AGENTS.md` as a compatibility wrapper for other agents unless it is specifically referenced.

## Invocation

Treat these as direct invocation and begin the initialize workflow:

- `/initialize`
- `use initialize`
- `use the initialize skill`
- clear equivalents where the user explicitly names this skill

Do not auto-trigger this skill from broad greetings, check-ins, or general conversation openers unless the user explicitly names or invokes the `initialize` skill.

If the user only wants a quick answer or to jump straight into work without the structured intake, answer directly without entering the initialize workflow.

## Blueprint Read

Field **f.) Blueprint Read** is a passive diagnostic.

When presenting the template, the agent must auto-fill field **f.)** by reporting which workspace blueprint files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, or any combination) it has either read from disk or had present in loaded conversation/project instructions before this response.

Do not read extra wrapper files solely to populate this field. For Claude, list `AGENTS.md` only when it was explicitly loaded, already present, or specifically referenced by another loaded instruction.

If a wrapper file such as `AGENTS.md` or `GEMINI.md` points to a canonical contract such as `CLAUDE.md`, report both the wrapper and the canonical contract when both were available before the template response.

If none was read from disk or present in loaded instructions, report: `None`.

A `None` result means the agent's platform configuration may not be working correctly. Flag it to the user.

## Template Output

After reading the blueprint, present this exact template for the user to copy, fill, and return:

```text
Tell Me More Boss!
a.) Main File We are working on First = ?
b.) List of Secondary Files Agent should look at/load = ...
c.) Summary(s) to read for context = ?
d.) Implementation Plan(s)/Task(s) to read = ?
e.) Miscellaneous Files to read = ?
f.) Blueprint Read = [auto-filled by agent: CLAUDE.md | AGENTS.md | GEMINI.md | None]
g.) What Mode Should we start the session in = Please run the skill for said mode or say "None/something that means no"
h.) Instructions or Prompts for what the agent should do in this next response = here please enter a prompt or a skill etc... LMK
```

After the template block, end the response with the mode footer `Mode = Initialize`. This footer appears only on this template-presentation response; Initialize is a one-shot intake tool, so the footer does not persist to the post-intake response or any later response. If another mode is active on this same response, apply the multi-mode footer rule from `CLAUDE.md`.

Field-by-field behavior:

- **a.) Main File** - user-filled. The primary file the session will focus on.
- **b.) Secondary Files** - user-filled. Additional files the agent should load into working context.
- **c.) Summaries** - user-filled. Summary files under `<project root>\Archive\Historical\Summaries\` or elsewhere to read for context.
- **d.) Implementation Plans/Tasks** - user-filled. Active plans under `<project root>\Archive\Live\Plans\` and/or pending tasks under `<project root>\Archive\Live\Tasks\` to read.
- **e.) Miscellaneous Files** - user-filled. Any other files the agent should read.
- **f.) Blueprint Read** - auto-filled by agent. Confirms which blueprint files the agent read from disk or had present in loaded conversation/project instructions. Not user-filled.
- **g.) Mode** - user-filled. The user specifies a mode skill to enter (e.g., `/debug`, `/brainstorm`) or says "None" for no mode.
- **h.) Instructions or Prompts** - user-filled. The prompt, skill invocation, or instruction for what the agent should do after loading context.

## Post-Intake Processing

After the user returns the filled template, the agent should:

1. **Load files (a-e):** Read or load the files specified in fields a through e. If a file path is unclear, ask for clarification. If a file cannot be found, report which files were loaded and which were not.

2. **Follow instructions (h):** Execute the prompt, skill, or instruction the user provided in field h. If the user invoked a skill, hand off to that skill's workflow.

3. **Confirm blueprint (f):** Confirm to the user which blueprint files were read. This was already auto-filled, but restate it briefly in the post-intake response.

4. **Enter mode (g):** If the user specified a mode, invoke that skill (e.g., enter Debug mode, Brainstorming mode). If the user said "None" or equivalent, continue without a mode sign-off.

## Boundaries

Do:

- read the project's canonical contract file(s) automatically upon invocation
- present the exact "Tell Me More Boss!" template
- auto-fill field f.) with the blueprint read confirmation
- load user-specified files after receiving the filled template
- follow the user's instruction from field h
- enter the requested mode from field g
- ask clarifying questions when file paths are unclear

Do not:

- edit product source files directly without explicit authorization
- generate product code by default
- skip the blueprint read step
- read extra wrapper files solely to populate the blueprint read field
- modify the template wording

## Validation

After creating or updating this skill itself:

- confirm local skill files exist
- confirm the exact "Tell Me More Boss!" template appears with fields a-h
- confirm the Blueprint Read section exists
- confirm the Post-Intake Processing section exists
- validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
