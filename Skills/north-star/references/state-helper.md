# North Star State Helper

`scripts/north_star_state.py` is the single source of truth for North Star lifecycle state, Full and Batch Mode transitions, the embedded Prompt Contract, per-turn pursuit timing, footer output, and terminal Base64 storage. Agents must never derive durations from timestamps or hand-edit encoded state.

## Core State

Every schema-6 run records:

- `initial_mode`: `full` or `batch`.
- `current_mode`: `full` or `batch`.
- `mode_transitions`: dated, reasoned, permanent Full-to-Batch changes.
- `prompt_contract`: `goal`, `constraints`, `format`, `definition_of_done`, and `failure`.
- `definition_of_done_complete`: evidence-supported DoD indexes.
- `failure_active`: currently active Failure indexes.
- `contract_review`: final evidence review of Constraints, Format, Failure, and DoD.
- `provenance`: mandatory Content owner, immutable Original writing agent, Created date, and Artifact role values for the canonical Field/Value table immediately after lifecycle.
- `change_log`: append-only attributed material changes rendered as the final human-readable section.
- `pursuits`, `active_pursuit`, `provisional`, corrections, evidence, notes, lifecycle, indicator, and navigation state.

A Full run changes permanently to Batch immediately when `checkpoint --another-iteration` records a known follow-up after pursuit 1, automatically before pursuit 2, when a material contract refinement follows pursuit work, or when a terminal run is reopened. Batch never silently returns to Full.

## Create

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" create \
  --workspace-root "<workspace-root>" \
  --subject "<Subject>" \
  --topic "<Topic>" \
  --writing-agent "<truthful agent family>" \
  --goal "<Prompt Contract GOAL>" \
  --pursuit "<approach>" \
  --mode full \
  --constraint "<constraint>" \
  --format "<required deliverable or output shape>" \
  --definition-of-done "<evidence-backed completion item>" \
  --failure "<invalid outcome or thing to avoid>"
```

Use `--mode batch` when the run begins in Batch Mode. `create` assigns the combined Live/Historical number, writes the mandatory Agent Provenance Field/Value table immediately after lifecycle, and stores the creation entry for the mandatory Agent Change Log rendered immediately before Base64. `init` accepts the same arguments, including required `--writing-agent`, for a structurally eligible existing artifact but refuses an ambiguous existing `## North Star` layout.

Creation does not start timing.

## Timing Lifecycle

A pursuit is one agent turn that actively advances the North Star:

1. Run `provisional-start` at the beginning of every unpaused active turn.
2. Run `pursuit-start` at the actual beginning of North Star work.
3. Work, verify, and checkpoint within the turn.
4. Run `pursuit-stop` when North Star work actually ends.
5. Report the helper-formatted latest pursuit and grand total exactly once.

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" provisional-start \
  --artifact "<live-path>"

python -X utf8 "<skill-dir>/scripts/north_star_state.py" pursuit-start \
  --artifact "<live-path>" \
  --batch "<batch label>" \
  --summary "<intended work>"

python -X utf8 "<skill-dir>/scripts/north_star_state.py" pursuit-stop \
  --artifact "<live-path>" \
  --acting-agent "<truthful agent family>" \
  --batch "<batch label>" \
  --summary "<completed work>"
```

Only one authoritative pursuit may be open. `pursuit-stop` appends the next sequential row, computes the duration and total, and discards the provisional timer. Starting pursuit 2 while current mode is Full first records the permanent transition to Batch.

When no North Star work occurred, run `provisional-discard`. When work occurred but precise timing was genuinely missed, run `provisional-commit --acting-agent "<truthful agent family>" --summary "<work>" --batch "<batch>"`; it creates one disclosed fallback row with `timing_source: "provisional_fallback"`. Never count both timing sources.

`--started-at` and `--ended-at` exist only for deterministic testing and controlled migration. Agents must not use them to manufacture time.

## Checkpoint And Contract Refinement

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" checkpoint \
  --artifact "<live-path>" \
  --acting-agent "<truthful agent family>" \
  --batch "<current batch>" \
  --next-action "<next action>" \
  --note "<evidence note>" \
  --verify-complete 1

python -X utf8 "<skill-dir>/scripts/north_star_state.py" checkpoint \
  --artifact "<live-path>" \
  --acting-agent "<truthful agent family>" \
  --another-iteration "<why another batch is required>"

python -X utf8 "<skill-dir>/scripts/north_star_state.py" refine \
  --artifact "<live-path>" \
  --acting-agent "<truthful agent family>" \
  --goal "<current goal>" \
  --constraint "<current constraint>" \
  --format "<current format>" \
  --definition-of-done "<current DoD item>" \
  --failure "<current Failure condition>" \
  --note "<reason>"
```

A checkpoint may mark supported DoD items, set `--failure-active <N>`, or clear resolved failure state with `--clear-failures`. Evidence-only checkpointing does not rewrite the Prompt Contract. Supplying any contract field to `refine` is a material replacement of that field; replacing DoD or Failure resets the corresponding completion or active indexes. Material refinement after pursuit work begins changes Full to Batch.

## Pause, Resume, Recovery, And Corrections

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" pause \
  --artifact "<live-path>" --acting-agent "<truthful agent family>" --reason "<user-approved reason>"

python -X utf8 "<skill-dir>/scripts/north_star_state.py" resume \
  --artifact "<live-path>" --acting-agent "<truthful agent family>"

python -X utf8 "<skill-dir>/scripts/north_star_state.py" recover \
  --artifact "<live-path>" --acting-agent "<truthful agent family>" --note "<interruption>"

python -X utf8 "<skill-dir>/scripts/north_star_state.py" pursuit-remove \
  --artifact "<live-path>" --acting-agent "<truthful agent family>" --number <N> --reason "<why it is invalid>"
```

Pause refuses open timing. Resume does not start timing. Recovery discards interrupted authoritative and provisional state without guessing a duration. Pursuit removal retains an auditable correction and renumbers later rows.

## Reopen

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" reopen \
  --artifact "<historical-path>" \
  --acting-agent "<truthful agent family>" \
  --batch "<reopened batch>" \
  --next-action "<next action>"
```

Reopen preserves run identity, permanent number, indicator, completed pursuits, totals, contract, and corrections; moves the artifact back to Live; and permanently enters Batch Mode.

## Inspect Authoritative State

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" status \
  --artifact "<path>" --json
```

Read `latest_pursuit`, `grand_total_seconds`, `grand_total_time`, open timing fields, mode fields, transition history, Prompt Contract, DoD completion, active Failure state, and final `contract_review` directly from helper output.

## Production Formatting

All formatter types refuse while authoritative or provisional timing remains open.

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" format-receipt \
  --artifact "<path>" --type <kind> [--subject <Subject>]
```

- `timing-statement`: `Pursuit <N>: <duration> — <summary>. Grand total: <duration>.`
- `fallback-disclosure`: the compulsory full-turn fallback disclosure.
- `mode-footer`: emits the exact selected-star Full, Batch, Paused, or `FINALIZED THIS TURN` final-line footer for the current status.
- `prompt-contract`: emits the five-part contract only for an explicit user opt-in or later request.
- `finalizer-receipt`: emits the verified completion receipt and absolute Markdown artifact link; finalized status and `--subject` are required.

## Finalize Or End

Close or discard all timing first.

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" finalize \
  --artifact "<live-path>" \
  --acting-agent "<truthful agent family>" \
  --evidence "<final evidence>" \
  --verify-complete <supported DoD number> \
  --constraints-verified \
  --format-verified \
  --failure-reviewed \
  --note "Finalized through finalize-north-star."

python -X utf8 "<skill-dir>/scripts/north_star_state.py" end \
  --artifact "<live-path>" --acting-agent "<truthful agent family>" --note "<why it ended>"
```

Finalization refuses open timing, missing DoD items, active Failure conditions, or absent Constraints, Format, or Failure review. It records `contract_review`, moves the same number from Live to Historical without overwrite, and adds no pursuit timing. `end` archives abandonment without claiming success. The retired `finish` command cannot bypass these gates.

## Terminal Storage Invariant

The generated Base64 comment is authoritative machine state. On every create, checkpoint, refine, pursuit, timing, pause, resume, recover, correction, reopen, finalize, or end mutation:

- exactly one Agent Provenance section immediately follows the lifecycle line and uses the canonical `Field | Value` table;
- exactly one Agent Change Log exists, is owned by encoded helper state, and is the final human-readable section;
- every material mutation requires truthful `--acting-agent` attribution and appends its change-log entry;
- exactly one `north-star:state-b64` marker follows the Agent Change Log inside the selected run;
- that state marker immediately precedes `north-star:run-end`; and
- `north-star:run-end` is the final nonblank line in the file.

Nothing may follow the managed block. Saves validate the complete lifecycle → provenance → North Star content → change log → Base64 → run-end order. Writes are atomic, UTF-8 and newline style are preserved, and lifecycle destinations use exclusive creation.

## Legacy Timing Tolerance

The existing pre-ledger timing normalization remains only to read earlier frozen timing safely. This upgrade does not rewrite historical North Stars, provide a bulk mode/contract migration command, or require historical artifacts to adopt the new schema.
