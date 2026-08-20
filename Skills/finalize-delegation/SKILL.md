---
name: finalize-delegation
description: Finalize an existing dispatched delegation record by verifying every assignment returned and was integrated, inspecting every named parent plan and/or task and confirming each is closed or carries its own explicit override, applying completed presentation styling, renaming _dispatched.md to _completed.md, moving the record from Archive\Live\Delegations to Archive\Historical\Delegations, and updating every named parent's Delegation pointer. Use when the user asks for /finalize-delegation, finalize delegation, close this delegation, mark delegation complete, this delegation is done, move the delegation to historical, or clear equivalents.
---

# Finalize Delegation

Close an existing dispatched delegation after the user confirms every assignment returned and the parent objective was integrated.

This skill only closes dispatched delegation records. It does not create, route, or dispatch delegations; use `delegate-this` for that.

A delegation is a lifecycle artifact, sibling to plans (`_active` → `_finalized`) and tasks (`_pending` → `_done`). Its **content** is immutable after dispatch — packets are never rewritten. Its **state** is not, and this skill is the only thing that changes it.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## UTF-8 Rule

Preserve UTF-8 when reading, rewriting, and moving the delegation record and the parent artifact. Never rely on the Windows default encoding.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/finalize-delegation`
- `use finalize-delegation`
- `finalize delegation`
- `finalize this delegation`
- `close this delegation`
- `mark delegation complete`
- `this delegation is done`
- `move the delegation to historical`
- clear equivalents where the user says a dispatched delegation is complete, closed, integrated, or done

If the user asks to create, route, or dispatch a delegation, stop and direct them to `delegate-this`.

## Required Review

Review only the sources needed to finalize the delegation safely:

1. The project's canonical contract (e.g. `CLAUDE.md`).
2. The user-referenced delegation record, if provided.
3. Existing `_dispatched.md` files under `<Workspace>\Archive\Live\Delegations\` when the user did not name the record.
4. **The parent plan and/or task named in the record's `Parent Artifacts` table.** This is mandatory — a delegation always has one.
5. Returned handoffs, session summaries, or mini plans/tasks only when needed to confirm every assignment returned.

Do not perform a broad workspace audit unless completion evidence genuinely requires it.

## Target Delegation Selection

Use the record the user explicitly references.

If the user does not reference one, inspect `<Workspace>\Archive\Live\Delegations\` for `_dispatched.md` files:

- If exactly one dispatched delegation exists, use it.
- If exactly one clearly matches the user's subject/topic/objective, use it.
- If multiple are plausible, ask which delegation to finalize.
- If none exists, stop and report that there is no dispatched delegation to finalize.

Never finalize a `_completed.md` file. Never touch a record outside the Delegations tree.

## Parent Artifact Gate

**A Mode A delegation always has a parent plan and/or task — and it may have both.** Before finalizing, resolve **every** parent named in the record's `Parent Artifacts` table and inspect each one's lifecycle state independently. Do not stop at the first parent you find.

Evaluate all named parents, then apply these rules:

- **Every named parent is closed** (`_finalized.md` / `_done.md`) → proceed.

- **Any named parent is still open** (`_active.md` / `_pending.md`) → **do not finalize silently.** A delegation is normally closed after its parents, because a parent is what proves the returned work was integrated. **Each open parent requires its own explicit override** — one override does not cover another. Ask, listing every open parent:

```text This delegation has open parents:

    1. <path>   (status: <ACTIVE / PENDING>)
    2. <path>   (status: <ACTIVE / PENDING>)

A delegation is normally finalized after its parents, since a parent proves the returned work was integrated. For EACH open parent above, tell me how to proceed:

a. Finalize that parent first (I will direct you to `finalize-plan` / `finalize-task`). b. Override — finalize this delegation anyway; that parent stays open for unrelated work. c. Stop. ```

  Only option (b) permits finalizing ahead of a parent, it must be an explicit user choice, and it must be granted **per parent**. Record every override in the completed record's notes, naming the parent it applies to.

- **Any named parent is missing or unreadable** → **stop and report.** Do not guess a parent, do not skip it, and do not finalize a record whose parents cannot all be verified. A missing parent is not an absent parent.

If the record names no parent at all, it predates the compulsory-parent rule, or it was a Mode B record that should never have been written. Report that, and ask the user to name the parent before proceeding.

## Completion Evidence Rules

Use evidence-based finalization.

Mark an assignment returned only when supported by at least one of:

- direct user confirmation
- current session evidence
- a returned handoff, session summary, or completed mini plan/task
- the record's own `Status` column, when the user confirms it is current

Walk the record's **Assignment Overview** row by row. Every row must be accounted for. For each, establish that the assignment **returned** and that its deliverable was **integrated** — those are two different things, and dispatch is neither.

If any assignment is unreturned, partially returned, unintegrated, conflicted, or unclear, **ask the user before finalizing.** Use the prompt in `Required Prompt For Ambiguous Returns`.

Do not silently mark all assignments returned because the user says "done."

Apply completed presentation language only when the evidence supports it.

## Conflict Check

The record's Return and Integration Instructions require that conflicting solutions be surfaced, not silently resolved. Before finalizing, confirm:

- no two returned assignments left contradictory changes on the same surface
- every conflict the orchestrator surfaced was resolved through the user or an explicit integrator decision
- the resolution is recorded somewhere durable — the parent artifact, a mini artifact, or a session summary

If an unresolved conflict remains, stop. A delegation with an open conflict is not complete.

## Finalized Delegation Presentation

Finalization converts a dispatched record into a completed record. Do a small presentation pass so the record reads as completed, not merely renamed. Preserve the original structure and style — **do not restyle the whole file, and never rewrite the assignment packets.** The packets are the immutable historical artifact.

Use these conventions where the matching sections exist:

- status line: `Status: COMPLETED ✅ — dispatched [YYYY-MM-DD], completed [YYYY-MM-DD].`
- if the dispatched date is unavailable: `Status: COMPLETED ✅ — completed [YYYY-MM-DD].`
- lifecycle line: `Delegation lifecycle: COMPLETED on [YYYY-MM-DD]. [Past-tense integration summary.]`
- `## Assignment Overview` → `## Assignment Overview ✅ Complete`
- in that table, each row's `Status` cell: `Dispatched` → `Returned & integrated`
- in that table, each row's `Actual model` cell: replace `User to select` with the model the user actually selected, when known. If it was never captured, write `Not recorded` — **never guess.**
- `## Return and Integration Instructions` → `## Return and Integration Instructions ✅ Complete`
- `## Global Stop Conditions` → leave as-is; it is a historical record of the constraints, not a checklist

Add a dated note under a `## Notes` section (create it at the end if absent) recording that the delegation was finalized under `finalize-delegation`, naming the parent artifact and its state, recording any user override from the Parent Artifact Gate, and noting that the session-summary / return-report family is now frozen.

Do **not** rewrite `## Assignment Packets`, `## Shared Context`, or `## Global Constraints`. Those are what the receiving agents acted on.

## Return-Report Freeze

Closing the delegation **freezes the entire session-summary / return-report family**. Every return report (the files ending in `Report.md` at the reserved child prefixes `Na.)`, `Nb.)`, …) and its append-only `## Delegation Ledger` becomes a closed historical artifact:

- No further `## Delegation Ledger` lines may be appended to any return report after the
  delegation is `_completed`.
- Existing report content and earlier feedback entries were already immutable;
  finalization does not change them, it just locks the ledger from new appends.
- The orchestrator/master summary (`N.)`) is likewise frozen.

This skill does **not** rewrite or renumber the return reports or their prefixes. The reserved child prefixes are permanent and are preserved verbatim. `session-summary` owns the report shape; this skill only enforces the freeze.

## File Rename And Move Rules

The record moves across the Archive's lifecycle boundary. Rename **and** move in one operation:

```text
From:  <Workspace>\Archive\Live\Delegations\<Subject>\N.) <Topic>_dispatched.md To:    <Workspace>\Archive\Historical\Delegations\<Subject>\N.) <Topic>_completed.md
```

Rules:

- **Preserve `N` exactly.** Do not renumber, and never reclaim a gap. `N` is lifecycle-agnostic and permanent — it was assigned once, across both the Live and Historical Subject folders, and it survives this move and any future reopen. The same applies to every **lowercase child prefix** (`Na.)`, `Nb.)`, …) on the delegation's mini artifacts and return reports: preserve them verbatim, never strip a suffix, never renumber.
- **Preserve the Subject folder name exactly, and never number it.** Subject folders are never numbered on either side.
- Create `Archive\Historical\Delegations\<Subject>\` if it does not exist, when file creation is allowed.
- If `N.)` collides with an existing file in the Historical Subject folder, **stop and ask.** Do not overwrite, delete, or silently renumber.
- Do not keep a duplicate at the Live path after a successful move.
- If the Live Subject folder is left empty by the move, leave it. Removing it is a separate, explicitly requested action.
- Do not delete or touch unrelated delegation files.

## Parent Pointer Update

After the move, **every** parent's `Delegation` pointer is stale — each still names the Live path. **Update all of them, or the link is broken.** A delegation naming both a plan and a task has two pointers to repair.

In the parent plan/task, rewrite:

```markdown
**Delegation:** `<Workspace>\Archive\Live\Delegations\<Subject>\N.) <Topic>_dispatched.md`
```

to:

```markdown
**Delegation:** `<Workspace>\Archive\Historical\Delegations\<Subject>\N.) <Topic>_completed.md` ✅
```

If the parent is already finalized (`_finalized.md` / `_done.md`), editing it to fix the pointer is permitted and expected — this is a pointer repair, not a reopening. Do not change the parent's status, lifecycle line, or any other content. Report the edit.

If the parent carries no `Delegation` field, add one under its `## Context` section rather than leaving the link one-directional.

## Required Prompt For Ambiguous Returns

When any assignment is unreturned, unintegrated, conflicted, or unclear, use this prompt shape:

```text
This delegation still has assignments that are not confirmed returned and integrated:

  <Wave> · <Platform> · <Role> — <Status>
  <Wave> · <Platform> · <Role> — <Status>

Before I finalize it, please confirm:

1. Which assignments have returned AND been integrated into the parent objective?
2. Which were abandoned, superseded, or explicitly cancelled?
3. Are any returned solutions still in conflict with one another?
4. Are you satisfied that this delegation can be closed after those updates?
```

Abandoned or cancelled assignments are recorded in the completed record's `## Notes` with the reason. They are not marked returned.

## Output Rules

After finalizing a delegation, report:

- the original dispatched path
- the final completed path
- the parent artifact path and its lifecycle state, plus any override the user granted
- completion evidence used, per assignment
- the parent pointer update
- any abandoned, cancelled, or deferred assignments
- validation performed

Do not paste the entire completed record into chat unless the user asks.

## Boundaries

Do:

- verify every assignment returned **and** was integrated before closing
- resolve and inspect **every** named parent artifact, always
- preserve `N.)`, the Subject folder name, and the assignment packets verbatim
- move the record Live → Historical and update **every** parent pointer in the same pass
- record overrides, abandonments, and conflicts in the completed record's notes, naming the parent each override applies to

Do not:

- create, route, or dispatch a delegation — that is `delegate-this`
- finalize a record when any named parent cannot be verified
- stop at the first named parent when the record names more than one
- treat one parent's override as covering another open parent
- finalize ahead of an open parent without an explicit user override for that parent
- renumber `N`, or reclaim a gap left by a completed record
- rewrite assignment packets, shared context, or global constraints
- guess an actual model that was never captured — write `Not recorded`
- renumber `N`, number a Subject folder, or overwrite a colliding Historical file
- leave the parent pointer at the stale Live path
- close a delegation with an unresolved conflict between returned solutions

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

This skill still owns every return, integration, parent, feedback-freeze, and completion gate. Before finalizing, discover same-stem `.md`, `.html`, and `.pdf` siblings for the delegation and its format-managed family members. Preflight every destination, apply completed status through the applicable format skill, rename every sibling's lifecycle suffix, and move the complete delegation set together without changing permanent prefixes.

HTML-only or PDF-only artifacts remain in that format; do not manufacture Markdown. Stop rather than finalize only part of a sibling set. Extension-only search and `Report.md` examples become format-neutral for this run.

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

After finalizing a delegation:

- confirm the dispatched source path no longer exists
- confirm the completed target path exists under `Archive\Historical\Delegations\<Subject>\`
- confirm the filename ends in `_completed.md` and retains its original `N.) ` prefix
- confirm the Subject folder name is unchanged and unnumbered
- confirm the file contains `Status: COMPLETED ✅` and a `Delegation lifecycle: COMPLETED` note
- confirm every Assignment Overview row shows a returned/integrated, abandoned, or cancelled status — none left `Dispatched`
- confirm no `Actual model` cell still reads `User to select`
- confirm the assignment packets are byte-for-byte unchanged from the dispatched record
- confirm **every** named parent's `Delegation` pointer names the new Historical path
- confirm every named parent was inspected, and that each open parent carried its own explicit override recorded in the notes
- confirm the session-summary / return-report family is frozen: no return report (files ending in `Report.md` at the reserved child prefixes) remains appendable, and no child prefix was stripped or renumbered
- confirm no unresolved conflict remains
- confirm UTF-8 text was used
- report any user overrides, abandoned assignments, or unresolved items

When creating or updating this skill itself, validate the folder-style skill with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
