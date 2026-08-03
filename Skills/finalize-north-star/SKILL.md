---
name: finalize-north-star
description: Finalize an in-progress North Star after verifying its objective and checklist evidence, change its lifecycle to FINALIZED, preserve its number and subject, and move it from Archive Live to Archive Historical. Use when the user invokes finalize-north-star or asks to close, complete, or finalize a North Star.
---

# Finalize North Star

Close a verified North Star deliberately. This is the only workflow that may
change a North Star from `IN PROGRESS` to `FINALIZED` or move it from
`Archive/Live/North Stars/` to `Archive/Historical/North Stars/`.

## Project Contract

Obey the active workspace contract, permissions, safety rules, and UTF-8
requirements. Finalization does not broaden the authorized task.

## Invocation

Treat these as direct invocation:

- `/finalize-north-star`
- `$finalize-north-star`
- `use finalize-north-star`
- `use the finalize-north-star skill`
- `finalize the North Star`
- clear equivalents that ask to close a live North Star

If the user asks to start, revise, continue, or resume a North Star, use
`north-star` instead.

## Required Dependency

This skill requires `north-star`, including
`scripts/north_star_state.py`. The helper owns the encoded lifecycle state,
checklist gate, status rewrite, suffix rename, and collision-safe move.

This skill inherits `north-star`'s compulsory selected-star footer, precise
pursuit-start/pursuit-stop scoping, helper-only timing authority, exactly-once
timing rule, and incomplete-response failure contract. Finalization narrows
those rules for lifecycle closure; it does not replace or weaken them.

If `north-star` or its helper is unavailable, stop and say:

> The `north-star` skill is required to finalize this artifact safely. Leave
> the North Star `IN PROGRESS`, install or load `north-star`, and run
> `finalize-north-star` again.

There is no manual fallback.

## Required Review

Review only what is needed:

1. the canonical workspace contract;
2. the referenced North Star, when supplied;
3. live North Stars under `Archive/Live/North Stars/` when none was named;
4. the North Star objective, verification checklist, evidence, checkpoint
   notes, constraints, boundaries, and stop conditions; and
5. referenced deliverables or validation output needed to prove completion.

Do not expand into a broad workspace audit.

## Pursuit Ownership And Scoping

Apply exactly one of these branches:

- **Standalone substantive finalization:** when this skill performs review or
  verification that advances the North Star, call `provisional-start` at turn
  open, `pursuit-start` at the actual beginning of that work, and
  `pursuit-stop` at its actual end. Keep unrelated same-turn work outside that
  interval.
- **Same-pass finalization:** when the parent North Star workflow already
  stopped the pursuit at the actual end of its work, use that closed pursuit.
  The parent's `pursuit-stop` already discarded the provisional timer. Do not
  start or stop a duplicate pursuit for finalization mechanics or its receipt.
- **No pursued work:** when this skill only checks existing helper state and
  performs lifecycle closure, discard the provisional timer with
  `provisional-discard` and do not manufacture a ledger entry.

No branch may leave an open provisional timer before finalization. If precise
scoping is genuinely impossible, use the disclosed provisional fallback rather
than guessing. The helper remains the only timing source in every branch; never
calculate duration from timestamps.

## Target Selection

Use the live North Star the user explicitly references.

Otherwise scan `Archive/Live/North Stars/` recursively for
`*_in_progress.md`:

- if exactly one exists, use it;
- if exactly one clearly matches the active objective, use it;
- if several are plausible, ask which one to finalize;
- if none exists, report that there is no in-progress North Star.

Never finalize a file already under `Archive/Historical/North Stars/`.

## Completion Gates

Finalization is evidence-based. Before closing:

1. Run the helper's `status --json` command.
2. Confirm the selected run is `in_progress` or `paused`.
3. Confirm the stated North Star objective is reached.
4. Confirm every verification item is checked from direct user confirmation,
   current-session evidence, or durable recorded evidence.
5. Confirm the constraints and boundaries were respected.
6. Confirm no stop condition represents an unresolved failure or blocker.
7. Confirm any substantive standalone pursuit was closed with `pursuit-stop`,
   or that same-pass finalization is using the parent's already-closed pursuit;
   in every case, confirm `active_pursuit` is `null` and `provisional` is
   `null`, and no duplicate or manufactured pursuit was added.

Existence, age, or a nearly complete checklist is not completion evidence.
Never invent evidence, silently check unsupported criteria, or extend pursuit
timing through finalization work.

If any required item is incomplete, ambiguous, blocked, or unsupported, leave
the file `IN PROGRESS` and ask for the missing evidence or an explicit,
recorded deferral. A deferral is valid only when the remaining work no longer
belongs to this North Star.

Before a refused or deferred response, stop any standalone pursuit this
finalizer opened and report that helper-derived pursuit statement exactly once.
Leave the artifact active or paused. Its selected star footer remains the final
line of every response and must state the current phase plus next action; when
paused, use the paused footer wording from `north-star` so resuming is obvious.
The footer disappears only after successful finalization.

## Finalization

For standalone substantive finalization, close the pursuit at the actual end
of review and verification:

```text
python -X utf8 "<north-star-dir>/scripts/north_star_state.py" pursuit-stop \
  --artifact "<live-north-star-path>" \
  --phase "<phase or run style>" \
  --summary "<one-line work actually completed>"
```

For same-pass finalization, do not run this command again when the parent
pursuit is already closed. For a no-pursuit finalizer, do not run it at all.
After every gate passes and helper state confirms no open pursuit, run:

```text
python -X utf8 "<north-star-dir>/scripts/north_star_state.py" finalize \
  --artifact "<live-north-star-path>" \
  --evidence "<final verification evidence>" \
  --note "Finalized through finalize-north-star."
```

The helper must:

- refuse finalization while a pursuit is open or a checklist item is unchecked;
- change the run status and visible header to `FINALIZED`;
- preserve the Subject, Topic, complete `N.)` prefix, ledger, and corrections;
- rename only `_in_progress.md` to `_finalized.md`;
- move the file from Live to the matching Historical Subject;
- refuse to overwrite or renumber on collision; and
- leave no duplicate on the Live side.

Finalization does not add timing. Read `latest_pursuit`,
`grand_total_seconds`, and `grand_total_time` from helper state after the move.
These are authoritative; never compute a duration or total from timestamps.
Use the current local date in the finalized presentation.
## Mandatory Completion Receipt

Every successful finalization must contain this exact populated statement:

```text
North Star <N> was verified and finalized. Pursuit <P>: <pursuit-duration> — <one-line summary>. Grand total: <grand-total>. <artifact link>
```

- `<N>` is the permanent North Star number.
- `<P>`, pursuit duration, and summary come from `latest_pursuit` after the
  final pursuit was closed. The helper-derived `latest_pursuit` may come from
  `pursuit-stop` (precise authoritative timing) or `provisional-commit`
  (disclosed full-turn fallback). Exactly-once reporting and helper-only
  arithmetic remain compulsory in both cases.
- `<grand-total>` comes from `grand_total_time` after finalization.
- `<artifact link>` points to the finalized Historical artifact.

If the artifact has only one pursuit, latest and grand total may be equal; both
labels remain explicit. If no completed pursuit exists, finalization is
incomplete because there is no pursued evidence-bearing turn to report.

### Pre-response completeness check

For successful finalization, confirm all of the following before replying:

1. any substantive pursued work has a matching `pursuit-start` and
   `pursuit-stop`, while same-pass or no-pursuit closure added no duplicate or
   manufactured entry;
2. no provisional timer or authoritative pursuit remains open;
3. `finalize` succeeded and the Live source is absent;
3. latest pursuit and grand total came from helper output, not inference;
4. the populated statement appears exactly once; and
5. no separate pre-finalization timing line duplicates it.

For refused or deferred finalization, confirm all of the following before
replying:

1. any pursuit opened by this finalizer was stopped and reported once, and any
   provisional timer was discarded;
2. no duration was calculated from timestamps and no duplicate or manufactured
   ledger entry was added;
3. the artifact remains `IN PROGRESS` or `PAUSED`; and
4. the selected active or paused star footer is the final line of the response.

A response is incomplete if pursued work lacks `pursuit-start`, if a provisional
timer remains open, if an entry is manufactured, if timing is agent-computed or
duplicated, or if an active or paused run's selected star footer is missing.

A continuous run completed in the current pass must be finalized in that same
pass when authority and evidence permit. Finalization itself does not extend
timing.
## No Manual Fallback

Only this skill, through the North Star helper, may finalize and move a North
Star. If the helper cannot complete the guarded operation, stop and report the
exact failure. Do not hand-edit the status, rename the suffix, or move the file
as a substitute.

## Output

Report:

- the original Live path;
- the final Historical path;
- the objective and checklist evidence used;
- any explicit deferrals;
- confirmation that the Live source no longer exists; and
- the exact mandatory receipt containing latest pursuit and grand total.

The timing statement appears exactly once, inside the receipt, sourced from
helper state. Do not emit a second duration line or paste the full artifact
unless the user asks.

When finalization is refused or deferred, report the missing gate, any
helper-derived pursuit statement required by this turn, and the next action.
Keep the selected active or paused star footer as the final line. Do not emit
the successful-finalization receipt.

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

This skill still owns every objective, checklist, evidence, and finalization
gate. Before finalizing, discover same-stem `.md`, `.html`, and `.pdf` siblings
and treat them as one North Star artifact set. Recover embedded native state
when the helper needs it, preflight every destination, apply final state, rename
the lifecycle suffix on every sibling, and move the complete set together.

An HTML-only or PDF-only North Star remains in that format; do not manufacture
Markdown. Stop rather than finalize only part of a sibling set. Extension-only
search and helper-path examples become format-neutral for this run.

## Validation

When creating or updating this skill:

- validate it with `quick_validate.py` in Python UTF-8 mode;
- smoke-test successful finalization of a fully verified North Star;
- confirm an unchecked item blocks finalization;
- confirm the number, Topic, Subject, indicator, timing, and evidence survive;
- confirm a Historical collision blocks without overwriting;
- confirm the Live source disappears only after a successful move; and
- confirm all global copies validate and have recursive byte parity.

Also prove each finalizer ownership branch:

- standalone substantive review starts and stops one precisely scoped pursuit;
- same-pass handoff consumes the parent's already-closed pursuit without a
  duplicate;
- a no-pursuit finalizer manufactures no ledger row;
- refused or deferred finalization closes and reports any pursuit it opened,
  preserves active or paused state, and retains the selected star footer;
- precise scoping excludes unrelated same-turn work; and
- the full-turn fallback is used only when needed and is explicitly disclosed.

When updating the **Mandatory Completion Receipt** contract, additionally
prove:

- finalization refuses an open pursuit;
- the pursuing turn is closed before finalization and excludes user waiting
  and finalization-reporting time;
- the receipt contains latest pursuit number, helper duration, one-line
  summary, and helper grand total exactly once;
- reopening, another pursuit, and re-finalization preserve earlier rows and
  report the new latest pursuit plus accumulated total; and
- omission, timestamp arithmetic, stale values, or duplicate timing makes the
  response incomplete.