---
name: north-star
description: Create and pursue a durable IN PROGRESS North Star under Archive Live until its Definition of Done is verified, with continuous or phased execution, stable star indicators, checkpoint timing, interruption recovery, and deliberate closure through finalize-north-star. Use when the user explicitly invokes north-star or asks to enter North Star mode.
---

# North Star

Create a dedicated live North Star artifact immediately, keep its objective
authoritative, and pursue it until verified or explicitly paused or ended.
North Star is standalone and does not require a platform-native goal feature.

## Project Contract

Obey the active workspace contract, permissions, safety rules, UTF-8
requirements, and file-edit restrictions. Persistence does not broaden
authority.

## Invocation

Treat these as explicit invocation:

- `/north-star`
- `$north-star`
- `use north-star`
- `use the north-star skill`
- `enter North Star mode`
- clear equivalents that explicitly name this skill

Do not activate merely because ordinary prose contains "goal", "objective",
or "north star".

## Establish The North Star

Resolve the standing objective in this order:

1. an objective supplied with the invocation;
2. the active user request;
3. a user-referenced existing live North Star;
4. one unambiguous objective and Definition of Done in current context.

If candidates conflict, ask which is authoritative. Otherwise infer and
proceed.

Before substantive execution define:

- the desired outcome and Definition of Done;
- a concrete verification checklist;
- pursuit approach and run style;
- constraints and scope boundaries;
- legitimate pause, blocker, and stop conditions; and
- Subject and Topic for the durable artifact.

Then acknowledge:

```text
North Star = [outcome and completion criteria]

Pursuit = [approach]

Verification = [checks and evidence]

Run style = Continuous | Phased
```

## Run Style

- **Continuous** — continue taking safe, authorized actions until the North
  Star is verified, blocked, or ready for deliberate finalization. If it is
  completed in the current pass, close the current pursuit and invoke
  `finalize-north-star` before replying.
- **Phased** — complete and verify an agreed phase, close that turn's pursuit,
  report the checkpoint, and wait while the North Star remains `IN PROGRESS`.

Honor an explicit choice. Otherwise default to Continuous when execution is
safe and independent; use Phased for approval gates, manual review, or
phase-governed work.

Both styles use the same per-turn ledger. In every turn that pursues the North
Star, timing opens when North Star work actually begins and closes when that
work actually ends. Unrelated same-turn work and time between user-facing
turns are never counted. A pursuit closure is not a formal pause and leaves
the run `IN PROGRESS`.
## Dedicated Artifact Lifecycle

Every new run gets its own artifact:

```text
In progress:
<Workspace>/Archive/Live/North Stars/<Subject>/N.) <Topic>_in_progress.md

Finalized:
<Workspace>/Archive/Historical/North Stars/<Subject>/N.) <Topic>_finalized.md
```

Lifecycle is expressed by location, filename suffix, visible status lines, and
the encoded helper state.

- New and resumed work is `IN PROGRESS` under `Live`.
- Only `finalize-north-star` may change it to `FINALIZED` or perform the
  successful-completion move. An explicitly abandoned run may be archived as
  `ENDED` through the helper's guarded `end` command.
- The complete `N.)` prefix, Subject, and Topic are permanent.
- North Star artifacts contain only North Star lifecycle and pursuit state.
  Do not embed the run into plans, tasks, prompts, reports, or summaries.
- There is no compact in-chat substitute when artifact creation is expected.
  If the workspace root or write permission cannot be resolved, pause and ask.

### Subject And Topic

Subject is a broad unnumbered category. Topic is a concise Title Case phrase
specific to the objective.

Use a user-supplied Subject or Topic when given. Otherwise infer them from the
request and existing subject folders. Ask only when a choice is genuinely
ambiguous or would materially alter organization.

### Permanent Number

Before creating a file, scan both matching subject folders:

- `Archive/Live/North Stars/<Subject>/`
- `Archive/Historical/North Stars/<Subject>/`

Capture `previous_max`, using `0` when neither contains a numbered file, then
assign `N = previous_max + 1`. Never recompute after writing, reclaim a gap,
renumber on finalization, or scan only one lifecycle side.

## Create, Resume, Or Reopen

Use the existing live artifact when the user points to it or current context
unambiguously resumes it. Recover its indicator, pursuit ledger, last
checkpoint, and next action before continuing.

When the user explicitly reopens a finalized or ended North Star, use
`reopen`. It moves the same numbered artifact from Historical to Live,
preserves every prior pursuit and correction record, clears terminal state,
and makes the next pursuit number sequential. Never create a replacement run
or assign a new number.

Otherwise create a new artifact immediately with the helper:

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" create \
  --workspace-root "<workspace-root>" \
  --subject "<Subject>" \
  --topic "<Topic>" \
  --objective "<North Star>" \
  --pursuit "<approach>" \
  --run-style continuous \
  --verification "<required check>" \
  --constraint "<constraint>" \
  --boundary "<scope boundary>" \
  --stop-when "<stop condition>"
```

The helper creates the folders, captures the combined namespace maximum,
writes `_in_progress.md` exclusively, and initializes the run block. Creation
and reopening do not start timing. In each pursued turn, call `pursuit-start`
when North Star work actually begins and `pursuit-stop` when it actually ends;
keep unrelated same-turn work outside that interval.

Use `scripts/north_star_state.py` for every lifecycle and timing mutation. Read
`references/state-helper.md` before using it. The helper is the only timing
authority.
## Mode Indicator

Each new run independently selects one indicator:

```text
0 = ⭐
1 = 🌟
2 = 🌠
3 = 💫
4 = ✨
5 = ✦
6 = ✧
7 = ✴️
```

Persist the index and symbol in the artifact and reuse that symbol throughout
the same run.

### Compulsory active footer

Whenever the North Star status is `IN PROGRESS`, the selected star footer is
compulsory on **every response**. This is unconditional: it applies to a
continuous full run, every turn of a phased run, responses that pursued the
North Star, and responses that did not pursue it. Run style is never an
exemption.

Footer rules:

- North Star only while active: `Mode = <selected-star>`
- Multiple modes while active: include the selected star exactly once.
- Put the footer on the final line of every response.
- While paused, extend that same final-line footer; do not invent a parallel
  status channel:
  - North Star only: `Mode = <selected-star> (PAUSED — say "resume North Star" to continue)`
  - Multiple modes: append ` (PAUSED — say "resume North Star" to continue)`
    to the combined-mode footer, with the selected star present exactly once.
- Emit the paused footer on every response while the run remains paused.
- Keep the applicable footer through checkpoints, phased handoffs, pauses,
  resumptions, interruptions, recovery, and turns containing unrelated work.
- Remove it only after successful finalization or an explicitly ended run.

Before sending any response while the run is active or paused, verify that the
footer is present, correct, and the true final line.
## Pursuit Loop

Pursuit timing is compulsory whenever an agent actually advances an
`IN PROGRESS` North Star. The provisional turn timer provides a full-turn safety
net; precise authoritative pursuit timing remains the preferred ledger source.

### Per-turn timing sequence

1. **Start provisional timer at turn open.** Call `provisional-start` at the
   beginning of every unpaused active turn, before other work when technically
   possible. Do not start provisional timing while paused, finalized, or ended.
2. **Start authoritative pursuit when work begins.** Call `pursuit-start` at the
   moment the agent begins North Star work in that turn, before reading, editing,
   testing, deciding, or otherwise acting for the objective.
3. **Keep unrelated work outside.** Work before the start or after the stop that
   does not advance the North Star must not enter its pursuit duration.
4. **Observe, act, and verify** only within authorization and boundaries.
5. **Checkpoint** phase, next action, notes, and newly proven checklist items.
6. **Stop when pursuit actually ends.** Call `pursuit-stop` as soon as North Star
   work ends in that turn, even if unrelated conversation or work follows before
   the final response. `pursuit-stop` discards the provisional timer
   automatically — authoritative timing wins.
7. **Report exactly once** using the values returned by `pursuit-stop` (precise
   timing) or `provisional-commit` (disclosed fallback), and the preserved
   statement shape.

Do not leave a pursuit or provisional timer open while waiting for the user.
Commentary about the active work remains inside the same pursuit; unrelated
commentary does not. A later user message begins a new opportunity for pursuit,
not automatic timing.

### Provisional fallback

When authoritative pursuit timing succeeds, the provisional timer is silently
discarded by `pursuit-stop`. When no North Star work occurs in a turn, call
`provisional-discard` before responding — this removes the timer without
creating a ledger row or timing statement.

When North Star work occurred but the precise authoritative timer was genuinely
missed, call `provisional-commit` to create exactly one disclosed full-turn
fallback row. The response must disclose that full-turn fallback scoping was
used. Never invent intermediate timestamps, backdate a helper command, or guess
a narrower interval.

Never count both intervals for the same turn. The provisional timer must not
remain open across a normal response handoff.

### Mandatory pre-response completeness check

Before every response while a North Star is active and unpaused, verify:

1. If North Star work was pursued this turn, either `pursuit-stop` succeeded
   (authoritative row recorded) or `provisional-commit` succeeded (fallback row
   recorded and disclosed). Never both.
2. If no North Star work occurred, the provisional timer was discarded via
   `provisional-discard` and no ledger entry was manufactured.
3. No provisional or authoritative timing state remains open.

Do not mark a criterion complete because time was spent or an action was
attempted. Record evidence first.

When work drifts away from the North Star — unrelated debugging, a tangent, or
an extended discussion that does not advance the objective — stop the current
pursuit before the drift and offer to formally pause the run. Never invoke
`pause` unilaterally. Formal pause is for intentional suspension across future
turns; it is not routine pursuit closure.
## Refine A Live Run

When the user changes the objective or completion criteria, preserve valid
progress and use the helper's `refine` command. Re-evaluate the checklist
rather than silently carrying completion marks onto changed criteria.

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" refine \
  --artifact "<live-path>" \
  --objective "<refined objective>" \
  --verification "<current required check>" \
  --verify-complete 1 \
  --phase "<current phase>" \
  --next-action "<next action>" \
  --note "<reason for refinement>"
```

## Progress Communication

Keep the user informed before major actions, after important findings, when the
approach changes, and during long tool work. Commentary updates remain within
the current pursuit. At a final response or phased handoff, report completed
work, evidence, changed artifacts, unresolved risks, and the exact continuation
point.

If the turn pursued the North Star, close its pursuit first and report the
helper-provided latest pursuit duration and grand total exactly once. Never
compute either value from timestamps.
## Active Pursuit Time Reporting

Active pursuit time is a ledger of discrete, correctly scoped North Star work
segments. There is no inactivity threshold, grace period, automatic exclusion,
or guessed pause. `pursuit-start` fires when North Star work actually begins in
a turn, and `pursuit-stop` fires when that work actually ends. Unrelated work
in the same turn stays outside the segment.

Each completed ledger row records:

- a sequential pursuit number;
- phase or run style;
- one-line work summary;
- helper-captured start and end timestamps for audit; and
- helper-computed duration.

The helper computes the grand total as the sum of completed pursuits. Agents
must never calculate durations or totals from timestamps. `status --json`
provides `latest_pursuit`, `grand_total_seconds`, and `grand_total_time`;
backward-compatible `active_pursuit_seconds_current` and
`active_pursuit_time_current` contain the same grand total.

### Reporting contract

For every response from a turn that pursued the North Star, report exactly one
timing statement using the production formatter:

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" format-receipt \
  --artifact "<live-path>" --type timing-statement
```

The formatter outputs the unchanged contract shape:
`Pursuit <N>: <duration> — <summary>. Grand total: <duration>.`

For fallback pursuits, also emit the disclosure:

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" format-receipt \
  --artifact "<live-path>" --type fallback-disclosure
```

The formatter refuses to produce response text while `active_pursuit` or
`provisional` timing remains open. Agents must use the formatter rather than
independently composing equivalent wording. Never compute a duration or total from
timestamps. If a turn performed no North Star pursuit, do not manufacture a ledger
entry or timing statement. The star footer remains compulsory because footer
presence follows active lifecycle, not whether that turn contained pursuit.

For continuous same-pass finalization, `finalize-north-star` owns the one timing
statement in its completion receipt. Do not print a separate pre-finalization
statement. For phased or deferred work, stop and report the pursuit while the
artifact remains `IN PROGRESS`.

### Incomplete North Star Response — Failure Conditions

A North Star response is incomplete when any of these conditions is true:

1. The timing statement is absent on a turn that pursued the North Star.
2. A duration or total was computed, inferred, backdated, or guessed instead
   of read from the helper-derived values returned by `pursuit-stop` or
   `provisional-commit`. A finalizer may re-read those same frozen values from
   helper state but must never recompute them.
3. More than one North Star timing statement appears in the response.
4. A ledger entry or timing statement was manufactured for a turn that
   performed no North Star pursuit.
5. `pursuit-start` was never called on a turn that did pursue the North Star
   (authoritative), or `provisional-commit` was never called after genuine
   pursuit with a missed precise timer (fallback). One of these two helper
   commands must produce the timing values for every pursued turn.
6. A provisional fallback pursuit was committed without explicit disclosure
   that full-turn fallback scoping was used.
7. Both an authoritative pursuit row and a provisional fallback row were
   recorded for the same turn.
8. An open provisional timer or authoritative pursuit remains unclosed before
   the response is sent.
9. The selected star footer is absent, incorrect, duplicated, or not the final
   line while the run is `IN PROGRESS` or `PAUSED`.

Do not send an incomplete response. Correct the helper lifecycle, reporting,
and footer before yielding control to the user.

### Explicit pause and interruption recovery

Routine pursuit closure is not `pause`. Explicit `pause` and `resume` remain
for a user-approved suspension across turns, and the paused footer remains
visible every turn. Neither command creates timing automatically.

If a turn is interrupted while a pursuit is open, `recover` discards the open
segment and records an auditable correction; it never guesses an end time or
counts the segment. Start a fresh pursuit when North Star work resumes.

### Corrections and reopening

Use `pursuit-remove --number <N> --reason <reason>` only when a ledger entry is
known to be wrong. The helper removes it, renumbers later pursuits, and appends
the removed entry and reason to `pursuit_corrections`. Never silently edit a
duration.

Reopening a terminal artifact preserves its completed pursuits and correction
history. The next pursued segment receives the next sequential number, and the
grand total continues from the preserved ledger.
## Accountability

For every checklist item:

- identify the check before claiming completion;
- collect current-session, durable, test, inspection, or user-confirmed
  evidence;
- verify constraints and boundaries too;
- leave unsupported items unchecked; and
- recheck uncertain or interrupted work.

Before closure, review the full objective and checklist. If anything lacks
evidence, continue or report the exact blocker.

## Checkpoint, Pause, Resume, Recover, And Status

Use the helper commands documented in `references/state-helper.md`:

- `provisional-start` opens the per-turn safety-net timer (idempotent);
- `pursuit-start` opens the precisely scoped North Star work segment;
- `pursuit-stop` closes it, appends one ledger row, and discards the provisional
  timer;
- `provisional-discard` removes the provisional timer without a ledger row;
- `provisional-commit` creates one disclosed full-turn fallback row;
- `checkpoint` records phase, next action, notes, and completed checks without
  changing timing;
- `pause` and `resume` preserve deliberate user-approved suspension and refuse
  open provisional or authoritative timing;
- `recover` discards an interrupted open pursuit and any open provisional timer
  without counting guessed time;
- `pursuit-remove` makes an auditable correction and sequentially renumbers;
- `reopen` returns a terminal artifact to Live with its ledger intact;
- `status --json` reports the latest pursuit, provisional state, and
  helper-computed grand total;
- `format-receipt --type <kind>` outputs the exact production user-facing text
  for timing statements, fallback disclosure, paused footers, and finalizer
  receipts — agents must use this rather than independently composing equivalent
  wording; and
- `end` archives an explicitly abandoned run without pretending it succeeded.

After interruption, inspect actual workspace state and reverify uncertain work.
Never blindly repeat destructive or non-idempotent actions.
## Deliberate Finalization

When every verification criterion has evidence:

- In a continuous, fully authorized pass, invoke `finalize-north-star`
  immediately when that skill is available and no user review gate remains.
  This is the **same-turn finalization** case: per **Active Pursuit Time
  Reporting**, the final active pursuit time is reported exactly once, in the
  final completion receipt — do not also emit a pre-finalization timing line
  in the same response.
- In a phased run, or when the user requested a review before closure, leave
  the artifact `IN PROGRESS` and hand off the exact finalization command. This
  is the **objective-met, finalization deferred** case: report the current
  cumulative active pursuit time in the ready-to-finalize handoff now, and let
  `finalize-north-star` report the final duration later in its receipt.
- If completion evidence is ambiguous, do not invoke the finalizer.
- If `finalize-north-star` is unavailable, leave the artifact live and tell the
  user to install or load it. Never finalize or move the file manually.

`finalize-north-star` verifies the objective and every checklist item, changes
the lifecycle to `FINALIZED`, and moves the file to the matching Historical
subject folder without changing its number. It owns the final completion
receipt, including the mandatory latest-pursuit and grand-total statement documented in its
own skill.

## Lifecycle

- **IN PROGRESS** — actively pursued or waiting at a phased handoff.
- **PAUSED** — intentionally inactive; indicator and timing are preserved.
- **FINALIZED** — verified and closed through `finalize-north-star`.
- **ENDED** — explicitly abandoned without claiming success and archived
  as `_ended.md` under the matching Historical Subject.

A blocker pauses or leaves the run in progress; it does not prove completion.

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule
to North Star artifacts and every checkpoint, refinement, pause, resume, recovery, end, or lifecycle update.

For every in-scope artifact:

- place an `## Agent Provenance` section near the top with `Content owner`,
  `Original writing agent`, `Created`, and `Artifact role`;
- use a stable truthful agent-family label such as `Codex Agent`, `Claude Agent`,
  `Antigravity Agent`, `Hermes Agent`, or `zCode Agent`;
- keep the original writing-agent entry immutable;
- keep an append-only `## Agent Change Log` near the bottom, recording the date,
  acting agent, action, and concise scope for every material edit;
- if a legacy artifact lacks reliable creator evidence, use `Not recorded` rather
  than guessing, then log the current agent's actual change; and
- treat copying or global synchronization as transport, not authorship.

Keep `Content owner` for now. In Uzo's personal artifacts it normally resolves
to `Uzo`; do not confuse content ownership with the agent that performed the
filesystem write. Do not inject provenance into product source, third-party
files, databases, generated caches, skill definitions, schema-sensitive or
machine-consumed files, or other operational files unless their schema
explicitly supports it.

## Durable Artifact Format Handling

This skill owns the North Star objective, checklist, permanent number, encoded
state, timing, checkpointing, location, and lifecycle. When co-invoked with
`html-this` or `pdf-this`, create only the requested durable format unless the
user requests multiple formats. Use a temporary native state representation
only as needed by `north_star_state.py`, then embed it through the format skill
and leave no durable Markdown intermediate.

On checkpoint, refine, pause, resume, recover, reopen, or end, recover the
embedded native source when necessary, apply the helper operation, and
regenerate every existing same-stem format sibling as one atomic artifact set.
Deduplicate siblings during number scans. This section overrides `.md`-only
examples only for co-invoked serialization; every encoded-state and lifecycle
gate remains mandatory.

## Validation

When creating or updating this skill:

- validate with `quick_validate.py` in Python UTF-8 mode;
- smoke-test creation under Live with combined Live/Historical numbering;
- smoke-test stable indicator reuse, refinement, checkpointing, pause/resume,
  recovery, status, ending, and a second independent run;
- confirm an unchecked item and an open pursuit each block finalization;
- smoke-test `finalize-north-star` moving a verified run to Historical;
- confirm helper edits remain inside the chosen artifact and collisions never
  overwrite; and
- confirm all global copies validate and have recursive byte parity.

When updating pursuit timing, reporting, or footer enforcement, additionally
prove all of the following:

- the named **Incomplete North Star Response — Failure Conditions** block
  exists and states all required timing failures: missing pursued-turn
  statement, computed rather than helper-derived duration, duplicate timing
  statements, manufactured no-pursuit entry, and missing `pursuit-start` or
  `provisional-commit`;
- footer omission is also an explicit failure;
- the selected star footer is compulsory on every active response in both
  continuous and phased styles, including turns with no pursuit;
- `pursuit-start` occurs when North Star work actually begins and
  `pursuit-stop` when it actually ends;
- unrelated same-turn work is excluded from the pursuit;
- imprecise scoping uses and discloses the full-turn fallback without guessed
  timestamps;
- every pursued response uses exactly one unchanged-shape timing statement
  sourced from the helper via `pursuit-stop` (precise) or `provisional-commit`
  (fallback), and a no-pursuit turn manufactures none;
- waiting between pursuits never changes the grand total;
- continuous same-pass finalization reports latest pursuit and grand total
  exactly once through `finalize-north-star`;
- explicit pause/resume remains user-approved and independent of pursuit
  closure;
- recovery discards an interrupted open pursuit without guessing duration;
- removing an incorrect pursuit records the removed entry and reason, then
  renumbers the remaining ledger sequentially; and
- reopening preserves all prior pursuits and begins with the next number.