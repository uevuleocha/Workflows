---
name: finalize-task
description: Finalize existing pending workspace housekeeping and admin task files by verifying Definition of Done evidence, resolving pending or blocked items with user confirmation, updating lifecycle/status text, and renaming _pending.md files to _done.md. Use when the user asks for /finalize-task, finalize task, mark task done, close pending task, rename pending task to done, or clear equivalents.
---

# Finalize Task

Finalize an existing pending workspace task after the user confirms the housekeeping or admin work is complete or satisfactory.

This skill only closes pending task files. It does not create or update pending tasks; use `imp-upd-task` for that.

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

If the user asks to create or revise a pending task, stop and direct them to `imp-upd-task`.

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

Never finalize a `_done.md` file. If the user wants to add work to a done task, direct them to `imp-upd-task` so the done task can be reopened gracefully.

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

## Definition Of Done Review

Before finalizing, inspect the task's `Definition of Done` section.

Finalize only when:

- each required Definition of Done item is satisfied, user-confirmed, or explicitly deferred out of scope
- each required validation item has passed, been user-confirmed, or been explicitly waived by the user
- any deferred work is recorded clearly

If the task lacks a `Definition of Done` section, ask the user for completion criteria before finalizing unless the user explicitly confirms that the task is done and no further criteria are needed.

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
- `## Definition of Done` -> `## Definition of Done ✅ Complete`
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

## File Rename Rules

Rename the pending file:

```text
{name}_pending.md
```

to:

```text
{name}_done.md
```

Do not keep a duplicate pending copy after a successful rename.

If the target `_done.md` file already exists, stop and ask before overwriting, deleting, or choosing another name.

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

## Validation

After finalizing a task:

- confirm the pending source path no longer exists
- confirm the done target path exists
- confirm the filename ends in `_done.md`
- confirm the file contains a done status or lifecycle note
- confirm a `Definition of Done` section exists, or record that the user explicitly waived it
- confirm the file contains `Status: DONE ✅` or record why the completed-style status was not applicable
- confirm the file contains a `Task lifecycle: DONE` note
- confirm a `Definition of Done ✅ Complete` section exists, or record that the user explicitly waived it or the original task used a different equivalent heading
- confirm completed task/checklist/validation headings use `✅ Complete` where applicable
- confirm no stale `Pending Phase` headings remain unless they are explicitly deferred or out of scope
- confirm UTF-8 text was used
- report any user-confirmed deferrals or unresolved items

When creating or updating this skill itself, validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
