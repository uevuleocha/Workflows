---
name: finalize-prompt
description: Finalize an existing pending prompt by verifying every Prompt Contract DEFINITION OF DONE item and every Verification Checklist item against evidence, confirming no FAILURE condition is active, applying executed presentation styling, and moving the file from its Subject folder under Archive\Live\Prompts\ to the matching Subject folder under Archive\Historical\Prompts\ while renaming its suffix from _pending to _executed and keeping its N.) prefix and Topic unchanged. Use when the user asks for /finalize-prompt, finalize prompt, mark prompt executed, close this prompt, this prompt is done, move the prompt to historical, or clear equivalents. This skill never creates, updates, or reopens a prompt; prompt-this owns that.
---

# Finalize Prompt

Close an existing **pending** prompt after the user confirms the work it asked for was actually done.

This skill only closes pending prompts. It does not create, update, or reopen them — use `prompt-this` for that.

A prompt's lifecycle is expressed by **location, its in-file `Status:` line, and a filename suffix** — `_pending` while Live, `_executed` once finalized:

```text
Pending:   <Workspace>\Archive\Live\Prompts\<Subject>\N.) <Topic>_pending.md
Executed:  <Workspace>\Archive\Historical\Prompts\<Subject>\N.) <Topic>_executed.md
```

**This skill is the only thing that may change PENDING → EXECUTED, move a prompt Live → Historical, or rename the suffix `_pending` → `_executed`.**

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, and approval gates defined there apply unchanged.

## UTF-8 Rule

Preserve UTF-8 when reading, rewriting, and moving the prompt file. Never rely on the Windows default encoding.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/finalize-prompt`
- `use finalize-prompt`
- `finalize prompt`
- `finalize this prompt`
- `mark prompt executed`
- `close this prompt`
- `this prompt is done`
- `move the prompt to historical`
- clear equivalents where the user says a pending prompt is complete, executed, or done

If the user asks to create, revise, extend, or **reopen** a prompt, stop and direct them to `prompt-this`.

## Required Review

Review only what is needed to finalize safely:

1. The project's canonical contract.
2. The user-referenced prompt, if provided.
3. Pending prompts under `<Workspace>\Archive\Live\Prompts\` when the user named none.
4. The prompt's own `## Prompt Contract` and `## Verification Checklist` — these are the authoritative gates.
5. Referenced deliverables, test output, session evidence, or validator results only as needed to confirm completion.

Do not perform a broad workspace audit.

## Target Prompt Selection

**Use the prompt the user references.** In practice the user names it, or the session makes it obvious. That is the normal path.

Only when neither holds, scan for pending prompts:

- **Scan recursively.** The Subject layer makes the tree two levels deep — a listing of `Archive\Live\Prompts\` returns Subject folder names and **zero** `.md` files. Descend into each Subject folder.
- If exactly one pending prompt exists, use it.
- If exactly one clearly matches the user's Subject/Topic/request, use it.
- If several are plausible, **ask** which to finalize.
- If none exists, stop and report that there is no pending prompt to finalize.

**Never finalize an already-executed prompt** — one already under `Archive\Historical\Prompts\`. To revise or rerun it, direct the user to `prompt-this`, which owns reopen.

## Completion Evidence Rules

Use evidence-based finalization. Mark a prompt executed only when supported by at least one of:

- direct user confirmation
- current-session evidence
- satisfaction of the prompt's `## Prompt Contract` DEFINITION OF DONE
- recorded tests, validators, inspections, or manual checks

**Never infer that a prompt was executed from its age, its location, or the fact that it exists.** A prompt sitting in `Live/` for a long time is a pending prompt, not a forgotten-but-done one.

If any deliverable is unverified, partial, or unclear, **ask before finalizing** (see `Required Prompt For Ambiguous Work`).

## Prompt Contract Review (Mandatory)

Every prompt created under `prompt-this` carries a `## Prompt Contract`. It is the authoritative completion gate. Walk it explicitly before finalizing:

- Check **each DEFINITION OF DONE item** against evidence. Mark it met, user-confirmed, or explicitly deferred out of scope.
- Check **each FAILURE condition**. Confirm none is active. If one is, do not finalize until it is resolved or the user waives it.
- Confirm the **GOAL** is met with evidence, and that the **CONSTRAINTS** were respected.

Finalize only when every DEFINITION OF DONE item is satisfied or explicitly deferred **and** no FAILURE condition remains active.

If a prompt predates the contract convention and has none, fall back to its `## Instructions` and `## Verification Checklist`, and ask the user for completion criteria if those are still ambiguous.

## Verification Checklist Review (Mandatory)

The contract *defines* success; the checklist *records* it. **Both are gates.** Walk every `## Verification Checklist` item:

- Confirm each is checked, or explicitly waived by the user with a reason.
- An unchecked item with no evidence and no waiver **blocks finalization**.

**The finalizer may check an item — but only on evidence.** Specifically:

- Check an item **only** when current-session evidence, durable execution evidence, or explicit user confirmation supports it.
- **Never assume, invent, or silently mark an unsupported item complete.**
- An unsupported item requires an explicit **waiver or deferral with a recorded reason**, or finalization **stops**.
- **A passing Prompt Contract is not, by itself, evidence that the checklist passed.** The contract defines success; the checklist records it.

## Handling Unfinished Work

If work remains and the user confirms it is deferred rather than complete:

- record it clearly under `## Notes` or a `Known Remaining Work` note
- do not mark deferred work complete
- finalize only if the remaining work no longer belongs to this prompt

If the user does not confirm whether work is complete or deferred, **stop and ask.**

## Executed Prompt Presentation

Finalization converts a pending prompt into a completed record. Do a small presentation pass so it reads as executed, not merely moved. **Preserve the original structure. Do not restyle the file.**

- status line → `Status: EXECUTED ✅ — created <YYYY-MM-DD>, finalized <YYYY-MM-DD>.`
- if the created date is unavailable → `Status: EXECUTED ✅ — finalized <YYYY-MM-DD>.`
- lifecycle line → `Prompt lifecycle: EXECUTED on <YYYY-MM-DD>. <Past-tense summary of what was done.>`
- `## Prompt Contract` → `## Prompt Contract ✅ Complete` — **only** once every DEFINITION OF DONE item is met or deferred and no FAILURE condition is active
- `## Verification Checklist` → `## Verification Checklist ✅ Complete`, checking each item **only where evidence supports it**. An item with no supporting evidence is left unchecked and carries a recorded waiver or deferral — or finalization stops.
- add a dated note under `## Notes` (create the section if absent) recording that the prompt was finalized under `finalize-prompt`, and any user-confirmed deferrals or waivers

**Never rewrite `## Prompt`.** The payload is the historical record of what was asked. `## What This Prompt Is`, `## Context`, and `## Instructions` are likewise left intact.

## File Move Rules

The prompt crosses the Archive's lifecycle boundary. Move it:

```text
From:  <Workspace>\Archive\Live\Prompts\<Subject>\N.) <Topic>_pending.md
To:    <Workspace>\Archive\Historical\Prompts\<Subject>\N.) <Topic>_executed.md
```

Rules:

- **Preserve `N.)` and the Topic exactly, and rename only the suffix `_pending` → `_executed`.** Do not renumber, do not reclaim gaps, do not alter the Topic. `N` is lifecycle-agnostic and permanent.
- **Preserve the Subject folder name exactly, and never number it.** Subject folders are unnumbered on both sides.
- Create `Archive\Historical\Prompts\<Subject>\` if it does not exist, when file creation is allowed.
- If a file with that `N.)` already exists in the Historical Subject folder, **stop and ask.** Do not overwrite, delete, or silently renumber.
- Do not keep a duplicate copy at the Live path after a successful move.
- If the Live Subject folder is left empty, leave it. Removing it is a separate, explicitly requested action.
- Do not touch unrelated prompt files.

## No Manual Fallback

**Only this skill may change a prompt from PENDING to EXECUTED, or move it Live → Historical.**

If this skill is unavailable to an agent, the correct behavior is to **stop**: leave the prompt `PENDING` exactly where it is, name the missing skill, and point the user at its install route. Never instruct a user to move or rename a prompt by hand, and never do it on their behalf. A manual move skips the Prompt Contract review and the Verification Checklist review — which is precisely how a prompt gets recorded as executed without ever having been executed.

## Required Prompt For Ambiguous Work

When deliverables are unverified, partial, or unclear:

```text
This prompt is not yet ready to finalize. Before I close it, please confirm:

1. Which of the Prompt Contract's DEFINITION OF DONE items are satisfied, and with what evidence?
2. Which Verification Checklist items are complete, and which should be waived?
3. Is any FAILURE condition still active?
4. Should any remaining work be deferred out of this prompt?
```

## Output Rules

After finalizing, report:

- the original Live path
- the final Historical path
- the completion evidence used, per DEFINITION OF DONE item
- Verification Checklist outcomes, including any waivers
- any user-confirmed deferrals or unresolved items

Do not paste the entire executed prompt into chat unless the user asks.

## Boundaries

Do:

- verify every DEFINITION OF DONE item **and** every Verification Checklist item against evidence
- confirm no FAILURE condition is active
- preserve `N.)`, the Topic, the Subject folder name, and the `## Prompt` payload verbatim, renaming only the suffix `_pending` → `_executed`
- move the file Live → Historical in the same pass as the status rewrite
- record deferrals, waivers, and the finalization date under `## Notes`
- stop on a Historical filename collision

Do not:

- create, update, or reopen a prompt — that is `prompt-this`
- finalize a prompt already under `Archive\Historical\Prompts\`
- offer or perform a manual move/rename fallback under any circumstance
- infer execution from a prompt's age, location, or mere existence
- treat a passing contract as evidence that the checklist passed
- check a Verification Checklist item that no evidence, durable record, or explicit user confirmation supports
- assume, invent, or silently mark an unsupported checklist item complete
- renumber `N`, reclaim a gap, or number a Subject folder
- rewrite `## Prompt`, `## What This Prompt Is`, `## Context`, or `## Instructions`
- restyle the file beyond the status, lifecycle, contract, checklist, and notes lines

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

Use the aligner's read-only `check` first. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. For safe padding-only findings, run `format` to a distinct nonexistent staged path, review the diff, adopt it, and rerun `check`. Resolve overflow, malformed, or ambiguous findings manually; stop on operational failure. Confirm the dependency is available before the final write, and never silently replace it with raw character counting. The portable rule below remains compulsory.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable artifact or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.


## Agent Provenance For Durable Artifacts

Finalization never replaces the original creator. Preserve the artifact's `## Agent Provenance` section exactly, including its immutable `Original writing agent` and `Original writing LLM` rows, then append a new entry to its `## Agent Change Log` naming the truthful acting agent, that agent's model, the lifecycle action, and the status/path or content scope changed. The change log is a five-column `Date and Time | Agent | Model | Action | Scope` table; stamp the new row `YYYY-MM-DD-HH:mm:ss` from the machine clock and never estimate it. Leave historical date-only rows exactly as written.

Preserve `## Agent Provenance` immediately after the artifact's opening block -- its title, status, and lifecycle lines -- and keep `## Agent Change Log` as the last section, or immediately above any section the artifact reserves for the last position.

Preserve the artifact's `## Feedback Section` exactly as found, **including an empty one**. Never prune a Feedback Section for carrying no entries, never renumber or rewrite an existing `### Feedback N` subsection, and never author a reply on another agent's behalf. It is an append-only cross-agent record, and finalization is not a reason to tidy it.

**Publication steps are never a closure gate.** A wiki sync, a `stage-commit-push` run, a GitHub push, or a submodule pointer bump must never block, defer, or fail finalization, and this skill never performs one itself. Those operations belong after the artifact reaches its final path -- finalization renames and moves the file, so syncing first leaves the wiki holding a synthesised copy of a path that no longer exists and dirties the repository again immediately. Where such an item appears in a DEFINITION OF DONE or Verification Checklist, report it, recommend a waiver, and close.

**An unticked box means not done.** Read a blank checkbox as incomplete, never as "done but awaiting confirmation." Do not supply the executing agent's ticks to make an artifact look finished. Where a box is unticked but its evidence is plainly present, report the discrepancy to the user rather than silently resolving it in either direction. Where an invented sync constraint is contradicted by the user's own authorization, report it and recommend a waiver rather than treating it as failure.

When same-stem Markdown, HTML, or PDF siblings exist, apply the same provenance history to the complete artifact set. If a legacy artifact lacks reliable creator evidence, record `Original writing agent: Not recorded` rather than guessing, and log the current finalizer's work. Do not add embedded provenance to product source, third-party files, databases, generated caches, skill definitions, schema-sensitive or machine-consumed files, or other operational files unless their schema explicitly supports it.

## Durable Artifact Format Handling

This skill still owns every Prompt Contract, Verification Checklist, evidence, and execution gate. Before finalizing, discover same-stem `.md`, `.html`, and `.pdf` siblings and treat them as one prompt artifact set. Preflight every destination, apply executed content/status through the applicable format skill, rename the lifecycle suffix on every sibling, and move the complete set together without changing the permanent prefix or Topic.

HTML-only or PDF-only prompts remain in that format; do not manufacture Markdown. Stop rather than finalize only part of a sibling set. Extension-only search and validation examples become format-neutral for this run.

## Checklist Tick Discipline

**Checklist Tick Discipline.** The executing agent ticks every DEFINITION OF DONE and Verification Checklist box its own evidence supports, in the same pass, and states the evidence for each. Leave a box unticked only when the claim is false, unevidenced, or ambiguous — and say which and why. An unticked box means "not done," never "done but awaiting someone else's confirmation." Independent verification re-checks the ticks; it does not supply them. A tick asserts what this pass did and evidenced; it does not assert that the result is proven correct in later production use.

As a finalizer, read an unticked box as **not done**. Never treat a blank box as "done, the executor was being cautious," and never supply the executor's ticks to make an artifact look complete. Where a box is unticked but its evidence is plainly present, report the discrepancy to the user rather than silently resolving it in either direction.

## No Invented Sync Constraints

**No Invented Sync Constraints.** Do not write "local master only," "no global sync in this pass," or any equivalent prohibition into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, FAILURE condition, or instruction unless the user asked for it. Sync authority belongs to the user and is granted at execution time, not predicted at authoring time. When the user later authorizes same-pass sync, an invented constraint turns a correct action into a permanently false checklist item that must be waived. If sequencing genuinely matters, express it as a default the user can override — "stop at the verified local master unless the user authorizes same-pass sync" — never as a completion criterion or failure condition.

This rule binds the authoring agent; it is **never** emitted as artifact text. Its presence is verified by the absence of invented sync constraints in produced artifacts, not by a section in them. It does not authorize syncing and does not change what counts as authorization.

## Non-Blocking Wiki And Git Items

**Non-Blocking Wiki And Git Items.** Do not write a wiki sync, a `stage-commit-push` run, a GitHub push, or a submodule pointer bump into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, or FAILURE condition as a completion criterion. Those operations belong **after** the artifact is finalized: finalization renames and moves the artifact, so syncing first dirties the repository again and leaves the wiki holding a synthesised copy of a path that no longer exists. If such an operation is genuinely worth recording, record it as an explicitly non-blocking follow-up — "after finalization, run `stage-commit-push`" — never as a box whose blank state blocks closure. A finalizer must never refuse or defer closure because a sync, push, or pointer bump has not happened.

**The carve-out.** This does not apply to an artifact **whose subject is** the wiki or Git work. A plan to build `wiki-sync` legitimately carries wiki items in its DEFINITION OF DONE, because there the wiki work *is* the deliverable rather than a publication step for it. The rule targets publication steps, not subject matter. Never strip a legitimate item from an artifact that is correct as written.

Like rule 2, this binds the authoring agent and is never emitted as artifact text.

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

After finalizing a prompt:

- confirm the Live source path no longer exists
- confirm the Historical target path exists under `Archive\Historical\Prompts\<Subject>\`
- confirm the `N.) ` prefix and the Topic are unchanged and the suffix was renamed `_pending` → `_executed`
- confirm the Subject folder name is unchanged and unnumbered
- confirm the file contains `Status: EXECUTED ✅` and a `Prompt lifecycle: EXECUTED` note
- confirm `## Prompt Contract ✅ Complete` and `## Verification Checklist ✅ Complete` appear only where the evidence supports them
- confirm every DEFINITION OF DONE item was reviewed and no FAILURE condition remains active
- confirm every Verification Checklist item is checked or explicitly waived with a reason
- confirm `## Prompt` is byte-for-byte unchanged from the pending file
- confirm a dated finalization note exists under `## Notes`
- confirm UTF-8 was used
- report any deferrals, waivers, or unresolved items

When creating or updating this skill itself, validate the folder-style skill with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`). Read the result from the exit code with stdout and stderr captured **separately**: exit `0` is valid; exit `1` with empty stderr is invalid; exit `1` with non-empty stderr means the validator crashed and validity is unknown. Never merge the streams.
