---
name: finalize-plan
description: Finalize existing active implementation plans by verifying completion evidence, resolving pending or debug-pending items with user confirmation, applying completed-plan presentation styling, updating lifecycle/status text, and renaming _active.md files to _finalized.md. Use when the user asks to finalize a plan, mark an implementation plan complete, close an active plan, rename an active plan to finalized, or says a plan is done/final/complete.
---

# Finalize Plan

Finalize an existing active implementation plan after the user confirms the work is complete or satisfactory.

This skill only closes active plans. It does not create or update active implementation plans; use `plan-this` for that.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/finalize-plan`
- `use finalize-plan`
- `finalize this plan`
- `mark this plan complete`
- `close this active plan`
- `rename active plan to finalized`
- `this implementation plan is done`
- clear equivalents where the user says an active implementation plan is complete, final, finalized, or done

If the user asks to create or revise an active implementation plan, stop and direct them to `plan-this`.

## Required Review

Review only the sources needed to finalize the plan safely:

1. The project's canonical contract (e.g. `CLAUDE.md`)
2. the user-referenced active plan, if provided
3. existing `_active.md` files under `<project root>\Archive\Live\Plans\` when the user did not name the plan
4. referenced verification results, session notes, or source files only when needed to confirm completion

Do not perform a broad repo audit unless the user asks or completion evidence genuinely requires it.

## Target Plan Selection

Use the plan the user explicitly references.

If the user does not reference a plan, inspect `<project root>\Archive\Live\Plans\` for `_active.md` files:

- If exactly one active plan exists, use it.
- If exactly one active plan clearly matches the user's project/component/task, use it.
- If multiple active plans are plausible, ask which plan to finalize.
- If no active plan exists, stop and report that there is no active implementation plan to finalize.

Never finalize a `_finalized.md` file.

## Completion Evidence Rules

Use evidence-based finalization.

Mark phases or checklist items complete only when supported by at least one of:

- direct user confirmation
- current session evidence
- existing plan status
- referenced verification or smoke-test results

If any `Pending`, `Debug Pending`, `Implemented / Debug Pending`, `Optional / Pending`, or unclear item remains, ask the user before finalizing.

For debug-pending or pending items, require user satisfaction or explicit confirmation before marking them complete.

Do not silently convert all pending work to complete just because the user says "final" if unresolved items remain.

Apply completed presentation language only when the evidence supports completion. Do not add `✅`, `Complete`, or finalized wording to a section that still contains unresolved, blocked, pending, debug-pending, reopened, deferred, or unclear work.

## Prompt Contract Review

Plans created under the current `plan-this` workflow carry a `## Prompt Contract` section (GOAL, CONSTRAINTS, FORMAT, DEFINITION OF DONE, FAILURE). When it exists, it is the authoritative completion gate. Before finalizing, walk it explicitly:

- Check each DEFINITION OF DONE item against completion evidence; mark it met, user-confirmed, or explicitly deferred out of scope.
- Check each FAILURE condition; confirm none is triggered. If any is active, do not finalize until it is resolved or the user waives it.
- Confirm the GOAL is met with evidence and that the CONSTRAINTS were respected.

Finalize only when every DEFINITION OF DONE item is satisfied or explicitly deferred and no FAILURE condition remains active. When applying completed styling, mark the contract's DEFINITION OF DONE complete (e.g. `## Prompt Contract ✅ Complete` or checked DoD items) and note in the finalize record that the contract was verified.

If the plan predates this convention and has no `## Prompt Contract` section, fall back to the `Definition Of Done Review` below.

## Definition Of Done Review

Before finalizing, inspect the plan's `Definition of Done` section when one exists (for plans carrying a `## Prompt Contract`, the Definition of Done is the contract's DEFINITION OF DONE clause — see **Prompt Contract Review** above).

Finalize only when:

- each required Definition of Done item is satisfied, user-confirmed, or explicitly deferred out of scope
- each required validation item has passed, been user-confirmed, or been explicitly waived by the user
- any deferred work is recorded clearly

If the plan lacks a `Definition of Done` section, use the plan's checklist, implementation phases, validation notes, and user confirmation as completion evidence. If those are still ambiguous, ask the user for completion criteria before finalizing unless the user explicitly confirms that the plan is done and no further criteria are needed.

## Delegation Check

Plans created under the current `plan-this` workflow carry a `**Delegation:**` line under `## Context`. It is a pointer, not a workflow. Read it before finalizing.

- **`N/A`, or the line is absent** (the plan predates the field) → nothing to do. Finalize normally. Do not mention delegation in the finalized plan.
- **The line names a delegation record** → the plan's work was divided among multiple agents, and that delegation must be closed too.

When a delegation is named, **still finalize the plan.** Then tell the user:

```text
This plan named a delegation record:

  <path>

Finalizing the plan does not close the delegation. Run `finalize-delegation` to verify
every assignment returned and was integrated, move the record to
`Archive\Historical\Delegations\`, and update this plan's Delegation pointer.
```

Record the delegation's state in the finalized plan's notes — for example, `Delegation still dispatched at finalization; user directed to finalize-delegation.`

**Never** invoke `finalize-delegation` yourself, and **never** read, edit, rename, or move the delegation record. This skill closes plans. It only points at the delegation so it cannot be silently orphaned.

If `finalize-delegation` is not loaded, **still finalize the plan**, then say that the delegation remains `_dispatched` and direct the user to install or load `finalize-delegation` and run it. **Do not imply that the record may be moved or renamed by hand.** This skill has no dependency on `finalize-delegation` and must not stall waiting for it.

## Handling Unfinished Work

If unfinished work remains and the user confirms it is deferred rather than completed:

- preserve or move it under `Open Items Explicitly Out Of Scope`, `Known Remaining Work`, or a clear next-plan note
- do not mark the deferred work complete
- only finalize if the remaining work no longer belongs to the current plan

If the user does not confirm whether pending work is complete or deferred, stop and ask.

## Finalized Plan Presentation

Finalization converts an active implementation plan into a completed record. Do a small presentation pass so the plan reads as completed, not merely renamed.

When the plan is fully complete, use these conventions where the matching sections exist:

- status line: `Status: FINALIZED ✅ - created [YYYY-MM-DD], finalized [YYYY-MM-DD].`
- if the created date is unavailable: `Status: FINALIZED ✅ - finalized [YYYY-MM-DD].`
- lifecycle line: `Plan lifecycle: FINALIZED on [YYYY-MM-DD]. [Past-tense completion summary.]`
- `## What Needs To Be Done` -> `## What Was Done ✅`
- `## Prompt Contract` -> `## Prompt Contract ✅ Complete` (only once every DEFINITION OF DONE item is met/deferred and no FAILURE condition is active)
- `## Implementation Checklist` -> `## Implementation Checklist ✅ Complete`
- `## Definition of Done` -> `## Definition of Done ✅ Complete`
- `## Validation` -> `## Validation ✅ Complete`
- `## Verification` -> `## Verification ✅ Complete`
- `## Testing` -> `## Testing ✅ Complete`
- `### Pending Phase ...`, `### Active Phase ...`, or `### Finalized Phase - ...` -> `### Finalized Phase ✅: ...`

Rewrite future-tense instructions into evidence-backed completion language when practical. For example, change validation bullets such as "Run validation..." into "Validation returned passing evidence." Keep this rewrite concise and avoid restyling unrelated prose.

If some work is explicitly deferred, preserve it under `Open Items Explicitly Out Of Scope`, `Known Remaining Work`, `Deferred Items`, or an equivalent section. Do not mark deferred sections complete unless the user confirms they are out of scope for the finalized plan.

Add a dated note under `## Notes / Reopen History`, `## Notes`, or an equivalent final section that the plan was finalized under `finalize-plan` and that completion styling was applied.

## Finalization Edits

Preserve the plan's original structure and style. Do not restyle the whole file.

When finalizing, update the plan as appropriate:

- apply the Finalized Plan Presentation conventions where the matching sections exist
- prefer `Status: FINALIZED ✅ - created [YYYY-MM-DD], finalized [YYYY-MM-DD].` for the status line
- prefer `Finalized Phase ✅: ...` for completed phase headings
- preserve context, locked decisions, critical files, verification notes, effort estimates, Definition of Done, and out-of-scope items while converting completed sections to completed-record language

- add or update a top lifecycle/status note such as `Status: FINALIZED / COMPLETE ✅`
- add or update a lifecycle line such as `Plan lifecycle: FINALIZED on [YYYY-MM-DD]`
- mark completed phases/items with standard Markdown completed checkboxes (`- [x]`) or the plan's existing completion marker style
- when a `Pending Phase`, `Active Phase`, `Debug Pending`, or `Implemented / Debug Pending` heading is fully complete, user-confirmed complete, or supported by completion evidence, rename it to `Finalized Phase ✅`
- do not rename pending, debug-pending, blocked, deferred, reopened, or unclear phase headings to finalized unless the user confirms they are complete or out of scope
- preserve context, locked decisions, critical files, verification notes, effort estimates, Definition of Done, and out-of-scope items
- record any user-confirmed deferrals clearly

Use the current local date for lifecycle text.

## File Rename And Move Rules

Finalization does two things to the file: it flips the lifecycle suffix **and**
moves the file from the `Live` side of the Archive to the `Historical` side.

**1. Flip the suffix.** Rename the active file:

```text
{name}_active.md
```

to:

```text
{name}_finalized.md
```

(Preserve the `_mini_` marker if present: `{name}_mini_active.md` →
`{name}_mini_finalized.md`.)

**2. Move Live → Historical.** Move the file from its `Live` plans folder to the
matching `Historical` plans folder, preserving the same `[Subject]` subfolder on
both sides:

```text
<project root>\Archive\Live\Plans\[Subject]\{name}_finalized.md
        ->  <project root>\Archive\Historical\Plans\[Subject]\{name}_finalized.md
```

Create the `Archive\Historical\Plans\[Subject]\` target folder if it does not
exist. **Preserve the file's `N.) ` prefix exactly — including any lowercase
child suffix** (`Na.)`, `Nb.)`, …). Finalization never renumbers and never
strips a child suffix. The prefix is assigned once for the life of the file
across the combined `Live` + `Historical` namespace, so the same prefix simply
follows the file into `Historical`. This applies equally on **reopen**: when a
finalized child plan is reopened back to `_active.md`, its complete lowercase
child prefix is preserved unchanged.

Do not keep a duplicate copy on the `Live` side after a successful move.

If the target `_finalized.md` file already exists in `Historical`, stop and ask
before overwriting, deleting, or choosing another name.

Do not delete unrelated plan files.

## Required Prompt For Ambiguous Pending Work

When pending/debug-pending work remains, use this prompt shape:

```text
This plan still has pending or debug-pending items. Before I finalize it, please confirm what should happen:

1. Which pending/debug items are now complete?
2. Which items should be deferred out of this plan?
3. Are you satisfied that this active plan can be finalized after those updates?
```

## Output Rules

After finalizing a plan, report:

- the original active path
- the final finalized path
- completion evidence used
- any user-confirmed deferrals or unresolved items
- validation performed

Do not paste the entire finalized plan into chat unless the user asks.

## Agent Provenance For Durable Artifacts

Finalization never replaces the original creator. Preserve the artifact's
`## Agent Provenance` section exactly, then append a new entry to its
`## Agent Change Log` naming the truthful acting agent, the finalization date,
the lifecycle action, and the status/path or content scope changed.

When same-stem Markdown, HTML, or PDF siblings exist, apply the same provenance
history to the complete artifact set. If a legacy artifact lacks reliable
creator evidence, record `Original writing agent: Not recorded` rather than
guessing, and log the current finalizer's work. Do not add embedded provenance
to product source, third-party files, databases, generated caches, skill
definitions, schema-sensitive or machine-consumed files, or other operational
files unless their schema explicitly supports it.

## Durable Artifact Format Handling

This skill still owns every Prompt Contract, checklist, evidence, delegation,
and closure gate. Before finalizing, discover same-stem `.md`, `.html`, and
`.pdf` siblings and treat them as one plan artifact set. Preflight every
destination, apply completed content/status through the applicable format
skill, rename the lifecycle suffix on every sibling, and move the complete set
together without changing the permanent prefix or Topic.

HTML-only or PDF-only plans remain in that format; do not manufacture Markdown.
Stop rather than finalize only part of a sibling set. Extension-only search and
validation examples become format-neutral for this run.

## Validation

After finalizing a plan:

- confirm the active source path under `Archive\Live\Plans\` no longer exists
- confirm the finalized target path exists under `Archive\Historical\Plans\[Subject]\`
- confirm the file was moved Live → Historical and its `N.) ` prefix (including any lowercase child suffix `Na.)`, `Nb.)`, …) is unchanged
- confirm the filename ends in `_finalized.md`
- confirm the file contains a finalized status or lifecycle note
- confirm the `## Prompt Contract` DEFINITION OF DONE items were reviewed and no FAILURE condition remains active, or record that the plan predates the Prompt Contract convention
- confirm a `Definition of Done` section exists (or the `## Prompt Contract` DEFINITION OF DONE clause for plans carrying a contract), or record that the user explicitly waived it or the original plan used a different equivalent completion section
- confirm the file contains `Status: FINALIZED ✅` or record why the completed-style status was not applicable
- confirm the file contains a `Plan lifecycle: FINALIZED` note
- confirm the `**Delegation:**` pointer was read; if it named a record, confirm the user was prompted to run `finalize-delegation` and that this skill did not touch the delegation file
- confirm a `Definition of Done ✅ Complete` section exists, or record that the user explicitly waived it or the original plan used a different equivalent heading
- confirm completed implementation/checklist/validation headings use `✅ Complete` where applicable
- confirm no stale `Pending Phase`, `Active Phase`, `Debug Pending`, or `Implemented / Debug Pending` headings remain unless they are explicitly deferred or out of scope
- confirm UTF-8 text was used
- report any user-confirmed deferrals or unresolved items

When creating or updating this skill itself, validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
