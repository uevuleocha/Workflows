# North Star State Helper

`scripts/north_star_state.py` is the single source of truth for North Star
lifecycle state, per-turn pursuit timing, and provisional turn-timer fallback.
Agents must never derive a duration from timestamps.

## Timing Model

A pursuit is one agent turn that actively advances the North Star:

1. Run `provisional-start` at the beginning of every unpaused active turn, before
   other work when technically possible.
2. Run `pursuit-start` at the moment North Star work actually begins.
3. Work, verify, and checkpoint within the same agent turn.
4. Run `pursuit-stop` immediately before the final response or handoff.
5. Report the returned latest pursuit and grand total exactly once.

No pursuit stays open while waiting for the user. There is no inactivity
threshold, grace period, automatic exclusion, or inferred pause. Time between
turns simply belongs to no pursuit.

Each completed row contains `number`, `phase`, `summary`, `started_at`,
`ended_at`, and `duration_seconds`. Fallback rows additionally carry
`timing_source: "provisional_fallback"`. Timestamps are audit inputs used only by
the helper. `grand_total_seconds` is the helper-computed sum of closed rows.

### Provisional Turn Timer

Every unpaused active North Star turn opens a provisional timer at turn start.
This is a safety net, not a competing accounting system:

- **Authoritative timing succeeds** → provisional is silently discarded when
  `pursuit-stop` closes the real pursuit.
- **No North Star work occurred** → `provisional-discard` removes the timer
  without creating a ledger row.
- **Work occurred but precise timing was missed** → `provisional-commit` creates
  exactly one auditable fallback row with `timing_source: "provisional_fallback"`.

Never count both intervals for the same turn. The provisional timer must not
remain open across a normal response handoff or successful finalization.

### Turn Lifecycle State Machine

```text
Turn opens (unpaused active) → provisional becomes active
  ├─ Real pursuit starts → authoritative active; provisional remains as fallback
  │   └─ Real pursuit stops → authoritative row appended; provisional discarded
  ├─ No pursuit → provisional discarded; no row
  └─ Pursuit occurred, precise timer missed → provisional committed as fallback row
```

## Create Or Initialize

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" create \
  --workspace-root "<workspace-root>" \
  --subject "<Subject>" \
  --topic "<Topic>" \
  --objective "<objective>" \
  --pursuit "<approach>" \
  --run-style continuous \
  --verification "<check>"
```

Use `init` with the same run arguments to add a run block to an eligible
existing artifact. Creation and initialization do not open a pursuit.

## Reopen A Terminal North Star

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" reopen \
  --artifact "<historical-path>" \
  --phase "<phase>" \
  --next-action "<next action>"
```

`reopen` preserves the run ID, number, indicator, completed pursuits, grand
total, and correction audit; moves the artifact to the matching Live subject;
and changes only terminal lifecycle state. It never creates a new North Star.

## Start And Stop Each Pursued Turn

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" pursuit-start \
  --artifact "<live-path>" \
  --phase "<phase or run style>" \
  --summary "<one-line intended work>"

python -X utf8 "<skill-dir>/scripts/north_star_state.py" pursuit-stop \
  --artifact "<live-path>" \
  --phase "<phase or run style>" \
  --summary "<one-line work actually completed>"
```

Only one pursuit may be open. `pursuit-stop` appends the next sequential row,
returns its duration and the grand total, and discards any open provisional timer.
Normal stop leaves the North Star `IN PROGRESS`; it is not a formal pause.

`--started-at` and `--ended-at` exist only for deterministic testing and
controlled migration. Agents must not use them to manufacture a duration.

## Provisional Turn Timer Commands

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" provisional-start \
  --artifact "<live-path>"

python -X utf8 "<skill-dir>/scripts/north_star_state.py" provisional-discard \
  --artifact "<live-path>"

python -X utf8 "<skill-dir>/scripts/north_star_state.py" provisional-commit \
  --artifact "<live-path>" \
  --summary "<one-line work actually performed>" \
  --phase "<phase or run style>"
```

### provisional-start

Opens one provisional turn timer. Must be called at the beginning of every
unpaused active turn, before other work when technically possible.

- Refuses when the North Star is `paused`, `finalized`, or `ended`.
- Refuses when an authoritative `active_pursuit` is already open — the
  provisional timer must be opened before substantive pursuit work begins,
  never after.
- Repeated calls are idempotent and do not create duplicate timers.
- Accepts `--started-at` only for deterministic testing.

### provisional-discard

Discards the open provisional timer without creating a ledger row. Use when:

- Authoritative pursuit timing succeeded (already handled automatically by
  `pursuit-stop`).
- No North Star work occurred this turn.

No error when no provisional timer is open; the command is a safe no-op.

### provisional-commit

Commits the open provisional timer as one disclosed full-turn fallback pursuit
row. Use only when North Star work occurred but the precise authoritative timer
was genuinely missed.

- Refuses when no provisional timer is open.
- Refuses when an authoritative `active_pursuit` is still open — close it first
  with `pursuit-stop` or `recover`.
- Creates a pursuit row with `timing_source: "provisional_fallback"`.
- Sets `provisional` to `null` after committing.
- Accepts `--ended-at` only for deterministic testing.

The committed row is a normal ledger entry for numbering, totals, and
finalization purposes. Its fallback origin remains visible in the encoded state
and in `status --json` output for later audit, correction, reopening, and
finalization operations.

## Checkpoint And Refine

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" checkpoint \
  --artifact "<live-path>" \
  --phase "<phase>" \
  --next-action "<next action>" \
  --note "<evidence note>" \
  --verify-complete 1

python -X utf8 "<skill-dir>/scripts/north_star_state.py" refine \
  --artifact "<live-path>" \
  --objective "<refined objective>" \
  --verification "<current check>" \
  --verify-complete 1 \
  --phase "<phase>" \
  --next-action "<next action>" \
  --note "<reason>"
```

Supplying `--verification` replaces the checklist. Checkpoint and refinement do
not open, close, or extend timing segments.

## Formal Pause And Resume

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" pause \
  --artifact "<live-path>" --reason "<user-approved reason>"

python -X utf8 "<skill-dir>/scripts/north_star_state.py" resume \
  --artifact "<live-path>"
```

Close the current pursuit and discard any open provisional timer before formal
pause. Pause/resume is reserved for an intentional suspension across future turns
and requires user agreement. Resume does not automatically begin timing; the next
pursued turn still calls `provisional-start` then `pursuit-start`.

## Recovery And Corrections

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" recover \
  --artifact "<live-path>" --note "<interruption>"

python -X utf8 "<skill-dir>/scripts/north_star_state.py" pursuit-remove \
  --artifact "<live-path>" --number <N> --reason "<why it is invalid>"
```

`recover` discards an interrupted open pursuit and any open provisional timer;
it never guesses an end time or counts an unverified interval.
`pursuit-remove` stores the removed entry and reason in `pursuit_corrections`,
then renumbers remaining rows sequentially. Never hand-edit durations.

## Inspect Authoritative State

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" status \
  --artifact "<path>" --json
```

Read:

- `latest_pursuit` for the most recently closed row (includes `timing_source`
  when the row is a provisional fallback);
- `grand_total_seconds` and `grand_total_time` for the sum of all rows;
- `active_pursuit` to detect an unclosed authoritative turn;
- `provisional` to detect an open provisional timer; and
- backward-compatible `active_pursuit_seconds_current` and
  `active_pursuit_time_current`, which equal the grand total.

The user-facing timing statement is:

```text
Pursuit <N>: <duration> — <summary>. Grand total: <duration>.
```

## Production Receipt Formatting

`format-receipt` is the production output contract for user-facing North Star
text. Agents must use it rather than independently composing equivalent wording.
All receipt types refuse when `active_pursuit` or `provisional` timing remains
open, consistent with the no-open-state-before-response invariant. `paused-footer`
additionally requires the North Star to be paused.

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" format-receipt \
  --artifact "<path>" --type <kind> [--subject <Subject>]
```

### Receipt types

| Type | Guard | Output |
|------|-------|--------|
| `timing-statement` | Refuses if `active_pursuit` or `provisional` is open | `Pursuit <N>: <duration> — <summary>. Grand total: <duration>.` |
| `fallback-disclosure` | Refuses if `active_pursuit` or `provisional` is open; refuses if latest pursuit is not a provisional fallback | `Full-turn fallback scoping was used for this pursuit — precise authoritative timing was missed.` |
| `paused-footer` | Refuses if `active_pursuit` or `provisional` is open; refuses if status is not `paused` | `Mode = <indicator> (PAUSED — say "resume North Star" to continue)` |
| `finalizer-receipt` | Refuses if `active_pursuit` or `provisional` is open; refuses if status is not `finalized`; requires `--subject` | `North Star <N> was verified and finalized. Pursuit <P>: <duration> — <summary>. Grand total: <total>. [<Subject> North Star <N>](<absolute-path>)` |

### Errors

- Every receipt type refuses with a clear error when `active_pursuit` or
  `provisional` is open.
- `fallback-disclosure` refuses when the latest pursuit is not a fallback.
- `paused-footer` refuses when the North Star is not paused.
- `finalizer-receipt` refuses when the artifact is not finalized or when
  `--subject` is missing.

## Finalize Or End

Close the current pursuit and discard any open provisional timer first.
`finalize` refuses an open pursuit, an open provisional timer, or an unchecked
verification item.

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" finalize \
  --artifact "<live-path>" \
  --evidence "<final evidence>" \
  --note "Finalized through finalize-north-star."

python -X utf8 "<skill-dir>/scripts/north_star_state.py" end \
  --artifact "<live-path>" --note "<why it ended>"
```

The legacy `finish` command is intentionally retired so completion cannot
bypass the guarded lifecycle paths.

## Backward Compatibility

When a pre-ledger artifact loads, the helper migrates its authoritative frozen
`active_duration_seconds`—or its prior helper-derived active total—into
Pursuit 1. Former pause and inactivity fields are retained under
`legacy_timing` for audit but no longer participate in new timing. Existing
pursuits, corrections, run ID, indicator, checklist, and lifecycle all survive.

## Storage And Safety

- State remains an encoded UTF-8 JSON comment inside the marked run block.
- Human-readable state includes the ledger and grand total.
- Writes are atomic and preserve UTF-8 BOM and dominant newline style.
- New files and lifecycle destinations use exclusive creation.
- Finalization and ending never overwrite or renumber a collision.