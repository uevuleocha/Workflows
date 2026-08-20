---
name: finalize-task
description: Finalize existing pending workspace housekeeping and admin task files by verifying Definition of Done evidence, resolving pending or blocked items with user confirmation, updating lifecycle/status text, and renaming _pending.md files to _done.md. Use when the user asks for /finalize-task, finalize task, mark task done, close pending task, rename pending task to done, or clear equivalents.
---

# Finalize Task

Finalize an existing pending workspace task after the user confirms the housekeeping or admin work is complete or satisfactory.

This skill only closes pending task files. It does not create or update pending tasks; use `task-this` for that.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/finalize-task`
- `use finalize-task`
- `finalize this task`
- `mark this task done`
- `close this pending task`
- `rename pending task to done`
- `this task is done`
- clear equivalents where the user says a pending housekeeping/admin task is complete, final, closed, or done

If the user asks to create or revise a pending task, stop and direct them to `task-this`.

If the user asks to finalize an implementation plan, use the relevant plan-finalization workflow instead.

## Required Review

Review only the sources needed to finalize the task safely:

1. Governing workspace instructions, if present.
2. The user-referenced pending task, if provided.
3. Existing `_pending.md` task files when the user did not name the task.
4. Referenced verification results, session notes, or workspace files only when needed to confirm the Definition of Done.

Do not perform a broad workspace audit unless the user asks or completion evidence genuinely requires it.

## Target Task Selection

Use the task the user explicitly references.

If the user does not reference a task, inspect the workspace's task directory for `_pending.md` files:

- If exactly one pending task exists, use it.
- If exactly one pending task clearly matches the user's area/component/task, use it.
- If multiple pending tasks are plausible, ask which task to finalize.
- If no pending task exists, stop and report that there is no pending task to finalize.

Never finalize a `_done.md` file. If the user wants to add work to a done task, direct them to `task-this` so the done task can be reopened gracefully.

## Completion Evidence Rules

Use evidence-based finalization.

Mark checklist items complete only when supported by at least one of:

- direct user confirmation
- current session evidence
- existing task status
- referenced verification or smoke-test results
- satisfaction of the task's `Definition of Done`

If any `Pending`, `In Progress`, `Blocked`, `Reopened`, `Optional / Pending`, or unclear item remains, ask the user before finalizing.

Do not silently convert all pending work to complete just because the user says "final" if unresolved items remain.

Apply completed presentation language only when the evidence supports completion. Do not add `✅`, `Complete`, or finalized wording to a section that still contains unresolved, blocked, pending, reopened, or unclear work.

## Prompt Contract Review

Tasks created under the current `task-this` workflow carry a `## Prompt Contract` section (GOAL, CONSTRAINTS, FORMAT, DEFINITION OF DONE, FAILURE). When it exists, it is the authoritative completion gate. Before finalizing, walk it explicitly:

- Check each DEFINITION OF DONE item against completion evidence; mark it met, user-confirmed, or explicitly deferred out of scope.
- Check each FAILURE condition; confirm none is triggered. If any is active, do not finalize until it is resolved or the user waives it.
- Confirm the GOAL is met with evidence and that the CONSTRAINTS were respected.

Finalize only when every in-pass DEFINITION OF DONE item is satisfied and no FAILURE condition remains active. Genuine later-use evidence belongs only under `## Deferred Real-World Verification` and never blocks closure. When applying completed styling, mark the contract's in-pass DEFINITION OF DONE complete (e.g. `## Prompt Contract ✅ Complete` or checked DoD items) and note in the finalize record that the contract was verified.

If the task predates this convention and has no `## Prompt Contract` section, fall back to the `Definition Of Done Review` below.

## Definition Of Done Review

Before finalizing, inspect the task's Definition of Done. For tasks created under the current workflow, that lives in the `## Prompt Contract` section's DEFINITION OF DONE clause — review it there (see **Prompt Contract Review** above). Older tasks may still carry a standalone `## Definition of Done` section; use that when present.

Finalize only when:

- each required Definition of Done item is satisfied, user-confirmed, or explicitly deferred out of scope
- each required validation item has passed, been user-confirmed, or been explicitly waived by the user
- any deferred work is recorded clearly

If the task lacks a `Definition of Done` section, ask the user for completion criteria before finalizing unless the user explicitly confirms that the task is done and no further criteria are needed.

## Delegation Check

Tasks created under the current `task-this` workflow carry a `**Delegation:**` line under `## Context`. It is a pointer, not a workflow. Read it before finalizing.

- **`N/A`, or the line is absent** (the task predates the field) → nothing to do. Finalize normally. Do not mention delegation in the finalized task.
- **The line names a delegation record** → the task's work was divided among multiple agents, and that delegation must be closed too.

When a delegation is named, **still finalize the task.** Then tell the user:

```text
This task named a delegation record:

  <path>

Finalizing the task does not close the delegation. Run `finalize-delegation` to verify
every assignment returned and was integrated, move the record to
`Archive\Historical\Delegations\`, and update this task's Delegation pointer.
```

Record the delegation's state in the finalized task's `## Notes / Reopen History` — for example, `Delegation still dispatched at finalization; user directed to finalize-delegation.`

**Never** invoke `finalize-delegation` yourself, and **never** read, edit, rename, or move the delegation record. This skill closes tasks. It only points at the delegation so it cannot be silently orphaned.

If `finalize-delegation` is not loaded, **still finalize the task**, then say that the delegation remains `_dispatched` and direct the user to install or load `finalize-delegation` and run it. **Do not imply that the record may be moved or renamed by hand.** This skill has no dependency on `finalize-delegation` and must not stall waiting for it.

## Handling Unfinished Work

If unfinished work remains and the user confirms it is deferred rather than completed:

- preserve or move it under `Known Remaining Work`, `Deferred Items`, or a clear next-task note
- do not mark deferred work complete
- only finalize if the remaining work no longer belongs to the current task

If the user does not confirm whether pending work is complete or deferred, stop and ask.

## Finalized Task Presentation

Finalization converts a pending task into a completed record. Do a small presentation pass so the task reads as completed, not merely renamed.

When the task is fully complete, use these conventions where the matching sections exist:

- status line: `Status: DONE ✅ - created [YYYY-MM-DD], finalized [YYYY-MM-DD].`
- if the created date is unavailable: `Status: DONE ✅ - finalized [YYYY-MM-DD].`
- lifecycle line: `Task lifecycle: DONE on [YYYY-MM-DD]. [Past-tense completion summary.]`
- `## What Needs To Be Done` -> `## What Was Done ✅`
- `## Prompt Contract` -> `## Prompt Contract ✅ Complete` (only once every DEFINITION OF DONE item is met/deferred and no FAILURE condition is active)
- `## Definition of Done` -> `## Definition of Done ✅ Complete` (older tasks with a standalone section)
- `## Task Checklist` -> `## Task Checklist ✅ Complete`
- `## Validation` -> `## Validation ✅ Complete`
- `### Pending Phase ...` or `### Finalized Phase - ...` -> `### Finalized Phase ✅: ...`

Rewrite future-tense instructions into evidence-backed completion language when practical. For example, change validation bullets such as "Run scan..." into "Scan returned zero hits." Keep this rewrite concise and avoid restyling unrelated prose.

If some work is explicitly deferred, preserve it under `Deferred Items`, `Known Remaining Work`, or an equivalent section. Do not mark deferred sections complete unless the user confirms they are out of scope for the finalized task.

Add a dated note under `## Notes / Reopen History` that the task was finalized under `finalize-task` and that completion styling was applied.

## Finalization Edits

Preserve the task's original structure and style. Do not restyle the whole file.

When finalizing, update the task as appropriate:

- apply the Finalized Task Presentation conventions where the matching sections exist
- prefer `Status: DONE ✅ - created [YYYY-MM-DD], finalized [YYYY-MM-DD].` for the status line
- prefer `Finalized Phase ✅: ...` for completed phase headings
- preserve context, scope boundaries, Definition of Done, validation notes, and reopen history while converting completed sections to completed-record language

- add or update a top lifecycle/status note such as `Status: DONE / COMPLETE ✅`
- add or update a lifecycle line such as `Task lifecycle: DONE on [YYYY-MM-DD]`
- mark completed checklist items with standard Markdown completed checkboxes (`- [x]`) or the task's existing completion marker style
- when a `Pending Phase` heading is fully complete, user-confirmed complete, or supported by completion evidence, rename it to `Finalized Phase ✅`
- do not rename pending, blocked, deferred, reopened, or unclear phase headings to finalized unless the user confirms they are complete or out of scope
- preserve context, scope boundaries, Definition of Done, validation notes, and reopen history
- record any user-confirmed deferrals clearly

Use the current local date for lifecycle text.

## File Rename And Move Rules

Finalization does two things to the file: it flips the lifecycle suffix **and** moves the file from the `Live` side of the Archive to the `Historical` side.

**1. Flip the suffix.** Rename the pending file:

```text
{name}_pending.md
```

to:

```text
{name}_done.md
```

**2. Move Live → Historical.** Move the file from its `Live` tasks folder to the matching `Historical` tasks folder, preserving the same `[Subject]` subfolder on both sides:

```text
<project root>\Archive\Live\Tasks\[Subject]\{name}_done.md
        ->  <project root>\Archive\Historical\Tasks\[Subject]\{name}_done.md
```

Create the `Archive\Historical\Tasks\[Subject]\` target folder if it does not exist. **Preserve the file's `N.) ` prefix exactly — including any lowercase child suffix** (`Na.)`, `Nb.)`, …). Finalization never renumbers and never strips a child suffix. The prefix is assigned once for the life of the file across the combined `Live` + `Historical` namespace, so the same prefix simply follows the file into `Historical`. This applies equally on **reopen**: when a done child task is reopened back to `_pending.md`, its complete lowercase child prefix is preserved unchanged.

Do not keep a duplicate copy on the `Live` side after a successful move.

If the target `_done.md` file already exists in `Historical`, stop and ask before overwriting, deleting, or choosing another name.

Do not delete unrelated task files.

## Required Prompt For Ambiguous Pending Work

When pending, blocked, reopened, or unclear work remains, use this prompt shape:

```text
This task still has pending, blocked, reopened, or unclear items. Before I finalize it, please confirm what should happen:

1. Which items are now complete?
2. Which items should be deferred out of this task?
3. Are you satisfied that this pending task can be finalized after those updates?
```

## Output Rules

After finalizing a task, report:

- the original pending path
- the final done path
- completion evidence used
- any user-confirmed deferrals or unresolved items
- validation performed

Do not paste the entire finalized task into chat unless the user asks.

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

**An unticked in-pass box means not done.** Read a blank in-pass checkbox as incomplete, never as "done but awaiting confirmation." Do not supply the executing agent's ticks to make an artifact look finished. Where an in-pass box is unticked but its evidence is plainly present, report the discrepancy to the user rather than silently resolving it in either direction. Unticked items under `## Deferred Real-World Verification` are preserved and reported but never block finalization. Where an invented sync constraint is contradicted by the user's own authorization, report it and recommend a waiver rather than treating it as failure.

When same-stem Markdown, HTML, or PDF siblings exist, apply the same provenance history to the complete artifact set. If a legacy artifact lacks reliable creator evidence, record `Original writing agent: Not recorded` rather than guessing, and log the current finalizer's work. Do not add embedded provenance to product source, third-party files, databases, generated caches, skill definitions, schema-sensitive or machine-consumed files, or other operational files unless their schema explicitly supports it.

## Durable Artifact Format Handling

This skill still owns every Prompt Contract, checklist, evidence, delegation, and completion gate. Before finalizing, discover same-stem `.md`, `.html`, and `.pdf` siblings and treat them as one task artifact set. Preflight every destination, apply completed content/status through the applicable format skill, rename the lifecycle suffix on every sibling, and move the complete set together without changing the permanent prefix or Topic.

HTML-only or PDF-only tasks remain in that format; do not manufacture Markdown. Stop rather than finalize only part of a sibling set. Extension-only search and validation examples become format-neutral for this run.

## Checklist Tick Discipline

**Checklist Tick Discipline.** The executing agent ticks every DEFINITION OF DONE and Verification Checklist box its own evidence supports, in the same pass, and states the evidence for each. Leave a box unticked only when the claim is false, unevidenced, or ambiguous — and say which and why. An unticked box means "not done," never "done but awaiting someone else's confirmation." Independent verification re-checks the ticks; it does not supply them. A tick asserts what this pass did and evidenced; it does not assert that the result is proven correct in later production use.

As a finalizer, read an unticked **in-pass** box as **not done**. Never treat a blank in-pass box as "done, the executor was being cautious," and never supply the executor's ticks to make an artifact look complete. Where an in-pass box is unticked but its evidence is plainly present, report the discrepancy to the user rather than silently resolving it in either direction. Unticked items under `## Deferred Real-World Verification` are explicitly non-blocking: preserve and report them, but do not refuse or delay finalization because they await later use or an external event.

## In-Pass And Deferred Real-World Verification

**In-Pass And Deferred Real-World Verification.** Classify every verification item before saving or finalizing an artifact:

- **In-Pass Verification:** evidence the executing agent can produce safely in the current pass, including deterministic tests, fixtures, simulations, and mock scenarios. These items remain blocking completion criteria and follow Checklist Tick Discipline.
- **Deferred Real-World Verification:** evidence that genuinely requires later live use, elapsed time, user adoption, or an external event. Put only these items in a separate `## Deferred Real-World Verification` checklist. They are non-blocking for finalization and may remain unticked after all in-pass completion criteria are met. State the future trigger and evidence required for each item.

Never defer an item the current agent can safely verify now merely to claim completion. Omit the deferred section when no genuine deferred item exists.

## No Invented Sync Constraints

**No Invented Sync Constraints.** Do not write "local master only," "no global sync in this pass," or any equivalent prohibition into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, FAILURE condition, or instruction unless the user asked for it. Sync authority belongs to the user and is granted at execution time, not predicted at authoring time. When the user later authorizes same-pass sync, an invented constraint turns a correct action into a permanently false checklist item that must be waived. If sequencing genuinely matters, express it as a default the user can override — "stop at the verified local master unless the user authorizes same-pass sync" — never as a completion criterion or failure condition.

This rule binds the authoring agent; it is **never** emitted as artifact text. Its presence is verified by the absence of invented sync constraints in produced artifacts, not by a section in them. It does not authorize syncing and does not change what counts as authorization.

## Non-Blocking Wiki And Git Items

**Non-Blocking Wiki And Git Items.** Do not write a wiki sync, a `stage-commit-push` run, a GitHub push, or a submodule pointer bump into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, or FAILURE condition as a completion criterion. Those operations belong **after** the artifact is finalized: finalization renames and moves the artifact, so syncing first dirties the repository again and leaves the wiki holding a synthesised copy of a path that no longer exists. If such an operation is genuinely worth recording, record it as an explicitly non-blocking follow-up — "after finalization, run `stage-commit-push`" — never as a box whose blank state blocks closure. A finalizer must never refuse or defer closure because a sync, push, or pointer bump has not happened.

**The carve-out.** This does not apply to an artifact **whose subject is** the wiki or Git work. A plan to build `wiki-sync` legitimately carries wiki items in its DEFINITION OF DONE, because there the wiki work *is* the deliverable rather than a publication step for it. The rule targets publication steps, not subject matter. Never strip a legitimate item from an artifact that is correct as written.

Like rule 2, this binds the authoring agent and is never emitted as artifact text.

## Exact Model Attribution

Before this skill creates or materially edits the first first-party durable artifact in a session, invoke `exact-model-confirmation-gate`. The gate must finish before any new `Original writing LLM` or current-run Agent Change Log `Model` value is written.

- Reuse the gate's verified identity for later durable-artifact writes while the exact model context, acting agent, task or thread, and execution environment remain unchanged. Do not ask again during that stable session.
- If authoritative current runtime or session evidence cannot establish the exact model, stop before the first write and ask the user once. Cache a valid answer only for the current stable session.
- Invalidate prospectively when the user reports a model change or authoritative evidence shows that the model, agent, task or thread, or execution environment changed. Never rewrite historical provenance or change-log rows.
- Keep reasoning effort, service tier, provider, model family, and agent family separate from exact identity. Reject labels such as `Medium`, `Priority`, `OpenAI`, `GPT-5`, and `Codex Agent` as substitutes for a full model identity.
- Do not inspect configuration, environment data, credentials, logs, transcripts, or unrelated files by default. Only the gate's genuinely unavoidable file-backed branch may invoke `tread-lightly`, request one model field, and accept it only when it authoritatively identifies the current session. This skill does not gain a blanket `tread-lightly` dependency.
- Use `Not recorded` only when no interactive user is available, the user cannot identify the model, or exact identity remains safely unresolvable after the permitted attempt.

If `exact-model-confirmation-gate` is unavailable and no verified stable-session result already exists, fail closed before the artifact write rather than guessing, silently using `Not recorded`, or performing broader discovery.

**Validation check:** Confirm the dependency is named in this skill and its README; the canonical caller block is byte-identical to `exact-model-confirmation-gate/references/canonical-caller-block.md`; first-write blocking, one-time confirmation, stable-session reuse, proactive change, context invalidation, identity separation, targeted lookup, unresolved fallback, and append-only history pass the shared deterministic suite; and no historical row was rewritten.

## Validation

- confirm the `## Checklist Tick Discipline` section is present and its rule text is unmodified;
- confirm the `## In-Pass And Deferred Real-World Verification` section is present; unticked in-pass items still block closure, while unticked `## Deferred Real-World Verification` items are preserved and reported without blocking finalization;
- confirm the `## No Invented Sync Constraints` section is present, and that a produced artifact contains **no** invented sync constraint in its DEFINITION OF DONE, Verification Checklist, CONSTRAINTS, or FAILURE sections;
- confirm the `## Non-Blocking Wiki And Git Items` section is present with its carve-out, and that a produced artifact contains **no** wiki-sync, push, `stage-commit-push`, or pointer-bump completion criterion;

After finalizing a task:

- confirm the pending source path under `Archive\Live\Tasks\` no longer exists
- confirm the done target path exists under `Archive\Historical\Tasks\[Subject]\`
- confirm the file was moved Live → Historical and its `N.) ` prefix (including any lowercase child suffix `Na.)`, `Nb.)`, …) is unchanged
- confirm the filename ends in `_done.md`
- confirm the file contains a done status or lifecycle note
- confirm the `## Prompt Contract` DEFINITION OF DONE items were reviewed and no FAILURE condition remains active, or record that the task predates the Prompt Contract convention
- confirm a `Definition of Done` is present (the `## Prompt Contract` DEFINITION OF DONE clause for tasks carrying a contract, or a standalone `## Definition of Done` section on older tasks), or record that the user explicitly waived it
- confirm the file contains `Status: DONE ✅` or record why the completed-style status was not applicable
- confirm the file contains a `Task lifecycle: DONE` note
- confirm the `**Delegation:**` pointer was read; if it named a record, confirm the user was prompted to run `finalize-delegation` and that this skill did not touch the delegation file
- confirm a `Definition of Done ✅ Complete` section exists, or record that the user explicitly waived it or the original task used a different equivalent heading
- confirm completed task/checklist/validation headings use `✅ Complete` where applicable
- confirm no stale `Pending Phase` headings remain unless they are explicitly deferred or out of scope
- confirm UTF-8 text was used
- report any user-confirmed deferrals or unresolved items

When creating or updating this skill itself, validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
