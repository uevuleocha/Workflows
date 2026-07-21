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

## Validation

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
