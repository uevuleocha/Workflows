---
name: finalize-brainstorm
description: Finalize an active Brainstorm only after evidence shows shared understanding, a user-approved North Star, complete capture, and explicit dispositions for contradictions and flags. Use when the user explicitly invokes /finalize-brainstorm, $finalize-brainstorm, use finalize-brainstorm, finalize this brainstorm, or a clear equivalent requesting Brainstorm lifecycle closure.
---

# Finalize Brainstorm

Close one exact active Brainstorm through evidence, explicit user acceptance,
and a collision-safe `_chivita` to `_fini` lifecycle transition.

This skill is the exclusive finalization owner. It does not conduct the
interview, create Brainstorms, invent missing answers, or repair an incomplete
capture silently.

## Project Contract

Obey the workspace's canonical contract, permissions, UTF-8 rules, and safety
boundaries. Finalization authority applies only to the exact Brainstorm the
user asked to close.

## Invocation

Treat these as direct invocation:

- `/finalize-brainstorm`
- `$finalize-brainstorm`
- `use finalize-brainstorm`
- `finalize this brainstorm`
- clear equivalents requesting Brainstorm lifecycle closure

Do not auto-trigger because a discussion sounds complete. The user must request
closure.

## Required Pair

This skill pairs with `brainstorm` and uses its deterministic helper:

`../brainstorm/scripts/brainstorm_state.py`

Resolve that sibling path from this skill's installed directory. If
`brainstorm` or the helper is missing, stop and report the dependency instead
of moving or rewriting the artifact manually.

## Resolve The Exact Chivita Artifact

1. Use an exact path supplied by the user when available.
2. Otherwise use the unique active artifact established by current session
   context.
3. Otherwise inspect the matching Live Brainstorms Subject.
4. If more than one candidate remains plausible, ask the user to choose.

The target must:

- live under `Archive/Live/Brainstorms/<Subject>/`;
- keep its permanent `N.)` prefix;
- end in `_chivita.md`; and
- contain valid Brainstorm state.

Never guess across collisions or finalize a `_fini.md` artifact again.

## Evidence Gates

Read the entire capture and inspect helper status. Finalization requires:

- a finalized North Star produced at convergence, not at opening;
- the user's confirmation of shared understanding;
- relevant decision-tree branches reviewed;
- every contradiction explicitly disposed;
- every Open Flag resolved, explicitly deferred with an owner, or accepted by
  the user as non-blocking;
- no flag marked blocking;
- an append-preserving Q&A and decision history;
- a clear next step or handoff; and
- current explicit user acceptance of finalization.

Do not treat a deferred or accepted flag as resolved. Preserve its real status
and owner in the Historical artifact.

## Blocked Finalization

If a gate fails:

1. Do not rename, move, or mark the artifact fini.
2. Report the smallest unresolved set.
3. Return interview gaps to `brainstorm`.
4. Leave the artifact `_chivita.md` in Live.

Never invent an answer, silently accept a flag, erase a contradiction, or mark
a checklist item complete merely to make finalization pass.

## Finalization Transaction

After every gate passes and the user explicitly accepts closure:

1. Reconfirm the exact source and computed destination.
2. Confirm the matching Historical Subject folder.
3. Confirm the destination does not already exist.
4. Invoke the Brainstorm helper's `finalize` command in Python UTF-8 mode.
5. Supply the user's acceptance as finalization evidence.
6. Let the helper update status, append lifecycle evidence, rename
   `_chivita.md` to `_fini.md`, and move Live to Historical atomically enough to
   refuse collisions.
7. Verify the source is absent and exactly one destination exists.
8. Report the permanent number and final absolute path.

The transition is:

`Archive/Live/Brainstorms/<Subject>/N.) <Topic>_chivita.md`

to:

`Archive/Historical/Brainstorms/<Subject>/N.) <Topic>_fini.md`

Subject, Topic, number, Q&A history, prior North Stars, contradictions, flags,
and lifecycle evidence remain intact.

## Mode Closure

Successful finalization ends Brainstorming mode for that completed cycle. Other
explicitly active modes remain active and retain their own footer entries.

If finalization is blocked, Brainstorming mode remains active unless the user
explicitly exits it.

## Later Breakthroughs

Do not reopen from this skill. A later breakthrough invokes `brainstorm`, which
owns reopening the same `_fini` artifact as `_chivita`, preserving its number
and prior history.

## Boundaries

Do:

- resolve one exact artifact;
- verify every gate from current evidence;
- require explicit user acceptance;
- preserve the full history;
- refuse collisions; and
- report the final path.

Do not:

- create a Brainstorm;
- continue the interview;
- set or rewrite the North Star;
- close unresolved blockers;
- overwrite Historical content; or
- globally synchronize skills.

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

This skill still owns every completion-evidence and closure gate. Before
finalizing, discover same-stem `.md`, `.html`, and `.pdf` siblings and treat
them as one Brainstorm artifact set. Preflight every destination, apply the
authorized completed content/status through the applicable format skill, rename
the lifecycle suffix on every sibling, and move the complete set together.

An HTML-only or PDF-only Brainstorm remains in that format; do not manufacture
Markdown. Stop rather than finalize only part of a sibling set. Extension-only
search and validation examples become format-neutral for this run.

## Validation

After creating or updating this skill:

- run the paired Brainstorm lifecycle fixtures in Python UTF-8 mode;
- validate this folder with `quick_validate.py`;
- confirm missing evidence blocks closure;
- confirm a destination collision blocks closure;
- confirm successful closure produces one `_fini.md` artifact;
- confirm permanent identity and history survive finalization and reopen; and
- validate every synchronized copy with recursive byte parity.
