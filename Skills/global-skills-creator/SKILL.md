---
name: global-skills-creator
description: Guided creation of reusable skills from a local master, with user questions, prompt/style collection, a proposed design checkpoint, and then optional sync across Codex, Claude, Antigravity, Hermes, and zCode global skill or workflow locations. Use when the user asks to create, design, promote, validate, or globally install a reusable skill and should be consulted before files are written.
---

# Global Skills Creator

Create a reusable skill from a local master skills folder, then optionally promote it to configured global locations for Codex, Claude, Antigravity, Hermes, and zCode. On Uzo's machine, the default local master is the Workflows workspace. On any other machine, first discover or ask for the user's local master skills folder and global skill install paths.

This is the guided/default variant. It must collect the user's prompt, draft, style notes, and design preferences before writing skill files. For autonomous create-and-sync behavior, use `global-skills-creator-auto`.

Use `session-summary/SKILL.md` from the resolved local master skills folder only as a structural muse when it exists: clear frontmatter, concise sections, required-input prompts, safety notes, and validation discipline. Do not copy the `session-summary` workflow unless the new skill actually summarizes sessions.

## Global Sync Integration (Mandatory)

This guided skill iterates with the user, and once the design is agreed and the local master is created and locally validated, it syncs the skill globally. Every global sync it performs MUST run through the `global-sync` skill (Mode A), so the same copy-and-validate workflow is used here as everywhere else. This skill and `global-sync` travel together; if you ever share this skill, ship `global-sync` with it.

1. After the local master is created and locally validated, invoke `global-sync` Mode A, pre-filled with the new skill name(s) and all configured global targets (Codex, Claude, Antigravity, Hermes, zCode). Do not re-ask the user for the target list.
2. `global-sync` owns the copy, the Hermes `Personal/` grouping, the zCode flat target, and the per-target validation. Do not duplicate that logic here beyond the availability-guard fallback below.

**Availability guard.** Before invoking, confirm `global-sync` is loaded.

- If it is NOT available, pause and tell the user:
  > The `global-sync` skill is not loaded. It is the mandatory global-sync step for this skill. Please make it available (e.g. add it from the local master or GitHub), or tell me to continue with the inline fallback.
- If the user continues without it, fall back to the **Inline Sync Fallback** below and note in the final report that `global-sync` was unavailable and the inline fallback was used.
- Never silently skip the sync.

### Inline Sync Fallback (only when `global-sync` is unavailable)

Reproduce `global-sync` Mode A inline for the new skill:

1. Resolve the global targets: Codex `~/.codex/skills/`, Claude `~/.claude/skills/`, Antigravity `~/.gemini/config/skills/`, Hermes `%LOCALAPPDATA%\hermes\skills\Personal\` (Uzo's machine: `C:\Users\Admin\AppData\Local\hermes\skills\Personal\`), and zCode `~/.zcode/skills/` (Uzo's machine: `C:\Users\Admin\.zcode\skills\`). If a target base directory is missing, stop and ask for the replacement path — never guess.
2. For each target: create the destination skill folder if missing (Hermes → under `Personal/`; zCode → flat under `~/.zcode/skills/`), then true-copy with `Copy-Item -Recurse -Force` (not `Write`) of `SKILL.md`, `agents/openai.yaml`, and any `scripts/`, `references/`, or `assets/`.
3. Ensure `...\hermes\skills\Personal\DESCRIPTION.md` exists (create with one-line frontmatter if missing).
4. Validate every copy with `quick_validate.py` (`-X utf8`), reading each result from the exit code — see `Reading the Validator's Result`.
5. Report that the inline fallback ran because `global-sync` was unavailable.

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
- `sync this skill to Codex, Claude, Antigravity, Hermes, and zCode`
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
9. Create local + all global copies?: Whether to sync the skill to all configured global locations or keep it local-only.

Skill Creation Intake

1. Skill Name =
2. Purpose =
3. Trigger Phrases =
4. Required Inputs =
5. Outputs =
6. Reference Files =
7. Resources Needed (scripts/references/assets/none) =
8. Validation Needed =
9. Create local + all global copies? =
```

If the user has already provided enough detail, do not proceed directly to file creation. First present the proposed skill design checkpoint from `Guided Design Rule` and wait for explicit approval or revisions.

## Default Path Stack

Resolve the path stack before creating or syncing. The user should normally have **one canonical local master skills folder per machine** unless they explicitly ask for multiple local masters. Help the user choose that folder when needed, and after it is chosen, treat it as the rule for that user's machine for future skill creation and sync work.

Preferred discovery order:

1. If the host workspace contains a `Skills/` or `skills/` folder and a canonical contract file such as `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`, treat the exact existing folder, preserving its casing, as the local master candidate. If both variants exist and no canonical contract identifies the intended master, stop and ask rather than guessing.
2. If no local master candidate is obvious, ask the user whether they want a local master folder, where it should live, and whether it should be the machine's single canonical local master.
3. Resolve global install candidates from the user's home directory:
   - Codex: `~/.codex/skills/`
   - Claude: `~/.claude/skills/`
   - Antigravity/Gemini: `~/.gemini/config/skills/`
   - Hermes: `%LOCALAPPDATA%\hermes\skills\Personal\` on Windows, or the user-confirmed Hermes skills category path
   - zCode: `~/.zcode/skills/`
4. If a target does not exist, stop and ask whether to create it, skip it, or use a different path.

Do not assume Windows paths on macOS or Linux. Translate examples into the host OS path style.

Maintainer defaults for Uzo's machine:

```text
Local master:
C:\Users\Admin\Uzzys Universe\MilkyWay\Tools\Workflows\Skills\[Skill-name]\SKILL.md

Codex global:
C:\Users\Admin\.codex\skills\[Skill-name]\SKILL.md

Claude global:
C:\Users\Admin\.claude\skills\[Skill-name]\SKILL.md

Antigravity global:
C:\Users\Admin\.gemini\config\skills\[Skill-name]\SKILL.md

Hermes global:
C:\Users\Admin\AppData\Local\hermes\skills\Personal\[Skill-name]\SKILL.md

zCode global:
C:\Users\Admin\.zcode\skills\[Skill-name]\SKILL.md
```

These maintainer defaults are known-good examples for Uzo's machine, not universal paths.

Create or update the local master first. After the local master is complete and locally validated, hand the propagation to `global-sync` Mode A (see `Global Sync Integration`), which copies it to Codex, Claude, Antigravity, Hermes, and zCode and validates every copy.

## Path Handling

Before creating or syncing, verify each resolved base directory exists:

- Local master skills folder
- Codex global skills folder
- Claude global skills folder
- Antigravity/Gemini global skills folder
- Hermes global skills folder (the `Personal/` category under the Hermes app-data skills directory)
- zCode global skills folder

If any directory is missing, stop and ask the user for the replacement path for that specific target. (When `global-sync` performs the sync, it runs these same checks; this list governs the inline fallback.)

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
8. Sync to the global locations by invoking `global-sync` Mode A (see `Global Sync Integration`), pre-filled with the new skill name and all five targets (Codex, Claude, Antigravity, Hermes, zCode). `global-sync` performs the copy and the per-target validation. Use the Inline Sync Fallback only if `global-sync` is unavailable and the user opts to continue.
9. Report files created, validations run, whether `global-sync` or the inline fallback performed the sync, replacement directories used, and any pending manual UI checks.

Ecosystem consistency rule: every folder-style skill must include `agents/openai.yaml` in the local master, Codex global copy, and Claude global copy. Claude may not require this file today, but the folder structure must remain mirrored unless the user later decides to remove `agents/` from all Claude global skills at once.

Prefer the official Codex `skill-creator` scripts when available. If Python or the scripts are unavailable, create the minimal folder structure manually and explain which validation could not run.

## Permission Behavior

If the user invokes this skill and approves creating a skill, treat that as approval to create:

- the local master copy
- the Codex global copy
- the Claude global copy
- the Antigravity global skill copy
- the Hermes global skill copy
- the zCode global skill copy

Codex and Claude must still follow their runtime permission model. If writing outside the workspace requires elevated approval, request it.

Antigravity must still follow the 2FA edit rule from `AGENTS.md` before creating or editing files:

```text
"make the edit" | "greenlight" | "approved" | "execute plan" | "go ahead" | "apply changes" | "do it" | "push to drive"
```

## Sync Rules

Syncing is owned by `global-sync` Mode A (see `Global Sync Integration`), which copies `SKILL.md`, `agents/openai.yaml`, and any `scripts/`, `references/`, or `assets/` into each target (Codex, Claude, Antigravity, Hermes under `Personal/`, and zCode), keeps the folder structure mirrored, ensures the Hermes `Personal/DESCRIPTION.md`, and validates every copy. Do not maintain a second copy of that logic here.

The **Inline Sync Fallback** in `Global Sync Integration` is the only exception, used solely when `global-sync` is unavailable and the user opts to continue.

Ecosystem consistency reminder: every folder-style skill must include `agents/openai.yaml` in the local master and every global copy, so the folder structure stays mirrored unless the user later decides to remove `agents/` from all copies at once.

## Validation Rules

### Required Portable Markdown Table Alignment

**Every skill, new or existing, that writes Markdown tables — whether into a durable artifact or into its own chat output — must carry a `## Markdown Table Alignment` section in its own `SKILL.md` with the complete rule below, plus a validation item that checks the rule remains present.** A skill that writes no Markdown tables anywhere is exempt; do not add the section to it as boilerplate.

When the new or updated skill creates or materially edits a file containing Markdown tables, it must also carry `## Deterministic Markdown Table Aligner Integration`, declare `markdown-table-aligner` as a dependency, and place the helper call at the real file-ownership boundary. Record chat-only, pure-serializer, delegated-writer, and helper-owned schema cases as exemptions instead of adding redundant calls.

The discriminator is table authorship, not artifact creation. A misaligned table in a chat briefing is exactly as broken as one inside a durable file, so a chat-only skill that emits tables is in scope, while an artifact-creating skill that never emits a table is not. When in doubt about whether a skill will ever write a table, include the section.

**Carrying the section is conditional; obeying the rule is not.** Every skill obeys pipe alignment in every table it writes — new or existing, being authored or being updated, whether or not it carries the section. There is no grandfather clause for older skills.

The rule to carry:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `→ see note [row-id]` (using that row's own identifier — its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

### Required Durable-Artifact Provenance

**Every skill, new or existing, that creates first-party durable artifacts must make those artifacts carry agent provenance and an append-only agent change log**, plus a validation item confirming both remain present.

- **Agent Provenance sits immediately after the opening block** — below the opening title, status, and lifecycle lines most artifacts begin with. Use the canonical two-column `Field | Value` table with exactly these rows, in this order: `Content owner`, `Original writing agent`, `Original writing LLM`, `Created`, `Artifact role`. Keep the `Content owner` field and record the original writing agent truthfully.
- **`Original writing LLM` is the model, not the agent.** `Claude Agent` is the agent family; `Claude Opus 5` is the LLM. They occupy separate rows and neither substitutes for the other. Use `Not recorded` when the model is genuinely unknown, never infer it from the agent label, and never backfill it into an existing artifact.
- **The Agent Change Log is the last section** — except where a skill already reserves the last position for something else, such as encoded machine state or a required trailer, in which case the change log goes immediately above that reserved section rather than displacing it. Render it as a five-column `Date and Time | Agent | Model | Action | Scope` table.
- **Change-log timestamps are read, never estimated.** Use `YYYY-MM-DD-HH:mm:ss` on a 24-hour clock, obtained from the machine clock at write time. Leave historical date-only rows exactly as written; a log carrying both shapes is correct, and the boundary between them is itself information.
- **A `Feedback Section` sits immediately above the change log** in any artifact that carries a DEFINITION OF DONE, a Verification Checklist, or checkboxes an executing agent later ticks. It is present and empty by default, and carries append-only numbered `### Feedback N - date - agent - descriptor` subsections. It is the cross-agent channel: an orchestrator, a verifier, and an implementer all write there and each reads what the others left, without sharing a session or a platform.
- **A skill that creates no first-party durable artifacts is exempt.** Never inject provenance into product source code, third-party files, databases, generated caches, skill definitions, schema-sensitive or machine-consumed files, or other operational files unless their schema explicitly supports it.

Always validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).

Run this validator for:

- local master folder
- Codex global folder
- Claude global folder, if it is folder-style and contains `SKILL.md`
- Antigravity global folder
- Hermes global folder (under `Personal/`)
- zCode global folder

Before sync, also inspect the local-master `SKILL.md` — new or existing — and determine whether the skill writes Markdown tables anywhere, in a durable artifact or in its own chat output. If it does, confirm its Markdown Table Alignment section and corresponding validation item are present. If it owns a file-based Markdown-table write or material edit, also confirm the deterministic-aligner integration and dependency declaration are present at the real ownership boundary. Missing applicable governance is a validation failure even when `quick_validate.py` passes. Record non-table and delegated/exempt cases explicitly.

When `global-sync` performs the sync, it runs this validation for every target; this list governs the inline fallback.

### Reading the Validator's Result

**Decide pass/fail from the process exit code, capturing stdout and stderr separately. Never by comparing `quick_validate.py`'s stdout text.**

The validator terminates its output with a platform-specific line ending — on Windows, `Skill is valid!\r\n`. A string comparison against `"Skill is valid!"` fails on a perfectly valid skill because of the trailing `\r`.

| Exit  | stderr    | Meaning                     | Action                                     |
| ----- | --------- | --------------------------- | ------------------------------------------ |
| `0`   | —         | Skill is valid              | Proceed.                                   |
| `1`   | empty     | Skill is invalid            | stdout explains why. Fix the skill, rerun. |
| `1`   | non-empty | Validator / runtime failure | Stop. Validity is unknown. Do not "fix".   |
| other | —         | Validation did not complete | Stop. Claim neither pass nor fail.         |

Exit `1` is **overloaded**: an invalid skill and a crash inside the validator produce the same code. **Non-empty stderr is the discriminator.** An invalid skill writes its reason to stdout and leaves stderr empty; a crashed validator writes its traceback to stderr and leaves stdout empty.

**Never merge the streams.** `2>&1` destroys the discriminator. Do not test for an English traceback substring either — that breaks under a non-English locale, a different Python implementation, or a validator that catches its own exception.

Treat a crash as *unknown validity*, never as a failed skill — "fixing" a skill that was never broken is the worse error.

Use stdout only to tell the *user* what went wrong. Never to decide.

## Skill Writing Guidelines

Keep the skill focused on the reusable procedure another agent needs. Do not add extra documentation files such as changelogs or install guides unless the user explicitly asks — with one mandatory exception: the README.

**README.md is compulsory for every skill.** Every skill ships a top-level `Skills/<name>/README.md` alongside `SKILL.md`, created in the same pass as the skill itself and mirrored to every global copy. Keep it very brief — a shelf label, not a second SKILL.md:

- a few sentences saying what the skill does and when to invoke it
- when the skill depends on, calls, or pairs with other skills, a short "Related skills" (ships-with/requires) list so an adopter taking the skill from a repo grabs the full set
- nothing else by default — no changelog, no install guide, no restated procedure

Do:

- keep `SKILL.md` concise and procedural
- create the mandatory brief `README.md` beside `SKILL.md` in the same pass
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
- decide pass/fail by matching the validator's stdout text rather than its exit code
- merge stdout and stderr (`2>&1`) when validating — it destroys the crash discriminator
- treat a crashed validator (exit `1` with non-empty stderr) as a failed skill
- copy another skill's task-specific workflow when it is only a style reference

## Final Status Format

After creating or updating a skill, report:

- local master path
- Codex global path
- Claude global path
- Antigravity skill path
- Hermes skill path (under `Personal/`)
- zCode skill path
- whether `global-sync` or the inline fallback performed the sync
- validations run and results
- replacement directories supplied by the user, or `none`
- manual UI checks still needed, if any

## Checklist Tick Discipline

**Checklist Tick Discipline.** The executing agent ticks every DEFINITION OF DONE and Verification Checklist box its own evidence supports, in the same pass, and states the evidence for each. Leave a box unticked only when the claim is false, unevidenced, or ambiguous — and say which and why. An unticked box means "not done," never "done but awaiting someone else's confirmation." Independent verification re-checks the ticks; it does not supply them. A tick asserts what this pass did and evidenced; it does not assert that the result is proven correct in later production use.

## No Invented Sync Constraints

**No Invented Sync Constraints.** Do not write "local master only," "no global sync in this pass," or any equivalent prohibition into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, FAILURE condition, or instruction unless the user asked for it. Sync authority belongs to the user and is granted at execution time, not predicted at authoring time. When the user later authorizes same-pass sync, an invented constraint turns a correct action into a permanently false checklist item that must be waived. If sequencing genuinely matters, express it as a default the user can override — "stop at the verified local master unless the user authorizes same-pass sync" — never as a completion criterion or failure condition.

This rule binds the authoring agent; it is **never** emitted as artifact text. Its presence is verified by the absence of invented sync constraints in produced artifacts, not by a section in them. It does not authorize syncing and does not change what counts as authorization.

## Non-Blocking Wiki And Git Items

**Non-Blocking Wiki And Git Items.** Do not write a wiki sync, a `stage-commit-push` run, a GitHub push, or a submodule pointer bump into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, or FAILURE condition as a completion criterion. Those operations belong **after** the artifact is finalized: finalization renames and moves the artifact, so syncing first dirties the repository again and leaves the wiki holding a synthesised copy of a path that no longer exists. If such an operation is genuinely worth recording, record it as an explicitly non-blocking follow-up — "after finalization, run `stage-commit-push`" — never as a box whose blank state blocks closure. A finalizer must never refuse or defer closure because a sync, push, or pointer bump has not happened.

**The carve-out.** This does not apply to an artifact **whose subject is** the wiki or Git work. A plan to build `wiki-sync` legitimately carries wiki items in its DEFINITION OF DONE, because there the wiki work *is* the deliverable rather than a publication step for it. The rule targets publication steps, not subject matter. Never strip a legitimate item from an artifact that is correct as written.

Like rule 2, this binds the authoring agent and is never emitted as artifact text.

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization. It must also require every future skill that owns file-based Markdown tables to carry this integration and the portable rule.

Use the aligner's read-only `check` first. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. For safe padding-only findings, run `format` to a distinct nonexistent staged path, review the diff, adopt it, and rerun `check`. Resolve overflow, malformed, or ambiguous findings manually; stop on operational failure. Confirm the dependency is available before the final write, and never silently replace it with raw character counting. The portable rule below remains compulsory.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Exact Model Attribution

Whenever this skill writes a new model identity, appends a current-run model value, or defines a workflow that does either:

- Record the full model identity actually used when it is safely available from current runtime or session metadata. Use a specific identity such as `GPT-5.6 Sol`, `GPT-5.6 Terra`, or `Claude Opus 5`; a family-only label such as `GPT-5`, `Claude`, or `Codex Agent` is not an acceptable substitute.
- Resolve identity in this order: current runtime or session metadata; a platform-provided current-model field; only then, when unavoidable, a field-minimized configuration lookup that returns the model field alone. Apply `tread-lightly` to any potentially sensitive configuration and never display, copy, search, diff, or log the whole configuration.
- Keep the agent family and model identity separate. Never infer an exact model from an agent label, provider name, stale configuration, or model family.
- Use `Not recorded` only when the exact identity genuinely cannot be established safely. Do not replace an available exact identity with `Not recorded` merely to avoid checking current runtime metadata.
- Preserve append-only history. Never rewrite a historical provenance or change-log value solely to improve an old model label; add a truthful current correction entry when correction is required.

**Validation check:** For every model value newly written in the current run, accept a full exact identity and the honest `Not recorded` fallback, but reject known ambiguous family-only labels or agent-family substitutions. Confirm model discovery exposed only the required model field and that no historical row was rewritten.

## Validation

- confirm the `## Checklist Tick Discipline` section is present and its rule text is unmodified;
- confirm the `## No Invented Sync Constraints` section is present, and that a produced artifact contains **no** invented sync constraint in its DEFINITION OF DONE, Verification Checklist, CONSTRAINTS, or FAILURE sections;
- confirm the `## Non-Blocking Wiki And Git Items` section is present with its carve-out, and that a produced artifact contains **no** wiki-sync, push, `stage-commit-push`, or pointer-bump completion criterion;
- confirm any newly created artifact-authoring skill requires the five-row Agent Provenance table, the five-column Agent Change Log, and a `## Feedback Section` above it;
- confirm every newly created or updated model-writing skill is classified as direct, delegated, or exempt; direct and delegated carriers must include the canonical `## Exact Model Attribution` block verbatim and its validation check;- confirm the `## Markdown Table Alignment` section and its validation check are present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells;
