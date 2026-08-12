---
name: north-star
description: Create and pursue a durable IN PROGRESS North Star under Archive Live until its Prompt Contract is verified, with Full or Batch Mode execution, automatic iteration transitions, stable star indicators, checkpoint timing, interruption recovery, and deliberate closure through finalize-north-star. Use when the user explicitly invokes north-star or asks to enter North Star mode.
---

# North Star

Create a dedicated live North Star artifact immediately, keep its objective authoritative, and pursue it until verified or explicitly paused or ended. North Star is standalone and does not require a platform-native goal feature.

## Project Contract

Obey the active workspace contract, permissions, safety rules, UTF-8 requirements, and file-edit restrictions. Persistence does not broaden authority.

## Invocation

Treat these as explicit invocation:

- `/north-star`
- `$north-star`
- `use north-star`
- `use the north-star skill`
- `enter North Star mode`
- clear equivalents that explicitly name this skill

Do not activate merely because ordinary prose contains "goal", "objective", or "north star".

## Establish The North Star

Resolve the standing objective in this order:

1. an objective supplied with the invocation;
2. the active user request;
3. a user-referenced existing live North Star;
4. one unambiguous objective and Definition of Done in current context.

If candidates conflict, ask which is authoritative. Otherwise infer and proceed.

Before substantive execution call `prompt-contracts` in embedded caller mode and define its full five-part contract:

- GOAL from the desired outcome;
- CONSTRAINTS from scope and safety boundaries;
- FORMAT from the required deliverables and output shape;
- DEFINITION OF DONE as concrete evidence-backed checks;
- FAILURE from invalid outcomes, blockers, and things to avoid;
- pursuit approach and run mode; and
- Subject and Topic for the durable artifact.

The user's explicit North Star invocation authorizes contract derivation for both Full and Batch Mode. Never stop to ask for separate Prompt Contract approval. Always embed the complete contract in the artifact. In-chat display is off by default: show it only when the user opts in during creation or later asks to see it. Suppressing chat display never permits an omitted or weakened artifact contract.

Then acknowledge:

```text
North Star = [GOAL and DEFINITION OF DONE]

Pursuit = [approach]

Prompt Contract = [embedded five-part contract]

Run mode = Full | Batch
```

## Run Mode

- **Full Mode** — attempt the complete authorized North Star immediately and continue until its Prompt Contract is verified, blocked, or ready for deliberate finalization. If it completes in pursuit 1, close that pursuit and invoke `finalize-north-star` before replying.
- **Batch Mode** — complete and verify one meaningful batch, close that turn's pursuit, report the checkpoint, and continue with later batches while the North Star remains `IN PROGRESS`. A batch may cover one plan phase, several phases, corrective iteration, or worthwhile new in-scope work; it is not one-to-one with a plan phase.

Honor an explicit choice. Otherwise default to Full Mode when execution is safe and independent; use Batch Mode for user review gates, manual work, or naturally separated batches.

Persist `initial_mode`, `current_mode`, and `mode_transitions`. A Full Mode run that needs another iteration changes permanently to Batch Mode immediately when that need becomes known after pursuit 1, or automatically before pursuit 2 begins. Material contract refinement after pursuit work begins also changes Full to Batch. Reopening terminal work enters Batch Mode. Never silently change Batch back to Full.

Both modes use the same per-turn ledger. In every turn that pursues the North Star, timing opens when North Star work actually begins and closes when that work actually ends. Unrelated same-turn work and time between user-facing turns are never counted. A pursuit closure is not a formal pause and leaves the run `IN PROGRESS`.
## Dedicated Artifact Lifecycle

Every new run gets its own artifact:

```text
In progress:
<Workspace>/Archive/Live/North Stars/<Subject>/N.) <Topic>_in_progress.md

Finalized:
<Workspace>/Archive/Historical/North Stars/<Subject>/N.) <Topic>_finalized.md
```

Lifecycle is expressed by location, filename suffix, visible status lines, and the encoded helper state.

- New and resumed work is `IN PROGRESS` under `Live`.
- Only `finalize-north-star` may change it to `FINALIZED` or perform the successful-completion move. An explicitly abandoned run may be archived as `ENDED` through the helper's guarded `end` command.
- The complete `N.)` prefix, Subject, and Topic are permanent.
- North Star artifacts contain only North Star lifecycle and pursuit state. Do not embed the run into plans, tasks, prompts, reports, or summaries.
- There is no compact in-chat substitute when artifact creation is expected. If the workspace root or write permission cannot be resolved, pause and ask.

### Subject And Topic

Subject is a broad unnumbered category. Topic is a concise Title Case phrase specific to the objective.

Use a user-supplied Subject or Topic when given. Otherwise infer them from the request and existing subject folders. Ask only when a choice is genuinely ambiguous or would materially alter organization.

### Permanent Number

Before creating a file, scan both matching subject folders:

- `Archive/Live/North Stars/<Subject>/`
- `Archive/Historical/North Stars/<Subject>/`

Capture `previous_max`, using `0` when neither contains a numbered file, then assign `N = previous_max + 1`. Never recompute after writing, reclaim a gap, renumber on finalization, or scan only one lifecycle side.

## Create, Resume, Or Reopen

Use the existing live artifact when the user points to it or current context unambiguously resumes it. Recover its indicator, pursuit ledger, last checkpoint, and next action before continuing.

When the user explicitly reopens a finalized or ended North Star, use `reopen`. It moves the same numbered artifact from Historical to Live, preserves every prior pursuit and correction record, clears terminal state, and makes the next pursuit number sequential. Never create a replacement run or assign a new number.

Otherwise create a new artifact immediately with the helper:

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" create \
  --workspace-root "<workspace-root>" \
  --subject "<Subject>" \
  --topic "<Topic>" \
  --writing-agent "<truthful agent family>" \
  --writing-llm "<truthful model name>" \
  --goal "<North Star goal>" \
  --pursuit "<approach>" \
  --mode full \
  --definition-of-done "<required check>" \
  --constraint "<constraint>" \
  --format "<required deliverable or output shape>" \
  --failure "<invalid outcome or thing to avoid>"
```

The helper creates the folders, captures the combined namespace maximum, writes `_in_progress.md` exclusively, and compulsorily creates all three mandatory sections. Immediately after the status and `North Star lifecycle:` lines, it renders `## Agent Provenance` as the canonical two-column `Field | Value` table with Content owner, Original writing agent, Original writing LLM, Created, and Artifact role. It renders `## Feedback Section` after the North Star content, and `## Agent Change Log` as the final human-readable section immediately before Base64 machine state, as a five-column `Date and Time | Agent | Model | Action | Scope` table. Creation and reopening do not start timing. In each pursued turn, call `pursuit-start` when North Star work actually begins and `pursuit-stop` when it actually ends; keep unrelated same-turn work outside that interval.

### Terminal Machine-State Invariant

The generated Base64 state is compulsory and makes the artifact self-contained. The section order is mandatory: status, lifecycle, Agent Provenance table, remaining human-readable North Star content, Feedback Section, Agent Change Log, Base64 state marker, then `north-star:run-end`. Agent Change Log is the final human-readable section; Base64 state is the final machine section. The Feedback Section sits immediately above the change log, never below it. The state marker must immediately precede `north-star:run-end`, and `north-star:run-end` must be the final nonblank line in the entire file. Nothing may follow it. Never hand-edit, relocate, or delete either mandatory provenance section or machine state; use the helper, which validates and normalizes every mutation.

Use `scripts/north_star_state.py` for every lifecycle and timing mutation. Read `references/state-helper.md` before using it. The helper is the only timing authority.
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

Persist the index and symbol in the artifact and reuse that symbol throughout the same run.

### Compulsory selected-star footer

The helper-produced selected-star footer is compulsory on **every applicable response**. This is unconditional for Full Mode, Batch Mode, paused work, refused or deferred finalization, and the response that successfully finalizes the North Star. Whether the turn contained pursuit work is never an exemption.

Footer rules:

- Full Mode: `Mode = <selected-star> North Star (FULL)`
- Batch Mode: `Mode = <selected-star> North Star (BATCH)`
- Multiple modes while active: include the selected star exactly once.
- Put the footer on the final line of every response.
- While paused, extend that same final-line footer; do not invent a parallel status channel:
  - North Star only: `Mode = <selected-star> North Star (<FULL|BATCH>, PAUSED — say "resume North Star" to continue)`
  - Multiple modes: append ` (PAUSED — say "resume North Star" to continue)`
    to the combined-mode footer, with the selected star present exactly once.
- Emit the paused footer on every response while the run remains paused.
- Keep the applicable footer through checkpoints, batch handoffs, pauses, resumptions, interruptions, recovery, and turns containing unrelated work.
- On the successful finalization response use `Mode = <selected-star> North Star (FINALIZED THIS TURN)` as the true final line. Remove it only on later unrelated responses or after an explicitly ended run.

Before sending any applicable response, run `format-receipt --type mode-footer` after closing timing, then verify that its output is present exactly once and is the true final line.
## Pursuit Loop

Pursuit timing is compulsory whenever an agent actually advances an `IN PROGRESS` North Star. The provisional turn timer provides a full-turn safety net; precise authoritative pursuit timing remains the preferred ledger source.

### Per-turn timing sequence

1. **Start provisional timer at turn open.** Call `provisional-start` at the beginning of every unpaused active turn, before other work when technically possible. Do not start provisional timing while paused, finalized, or ended.
2. **Start authoritative pursuit when work begins.** Call `pursuit-start` at the moment the agent begins North Star work in that turn, before reading, editing, testing, deciding, or otherwise acting for the objective.
3. **Keep unrelated work outside.** Work before the start or after the stop that does not advance the North Star must not enter its pursuit duration.
4. **Observe, act, and verify** only within authorization and boundaries.
5. **Checkpoint** the current batch, next action, notes, newly proven DoD items, and any active or cleared Failure conditions. If another iteration is already known after pursuit 1, pass `--another-iteration "<reason>"` so Full changes to Batch immediately.
6. **Stop when pursuit actually ends.** Call `pursuit-stop` as soon as North Star work ends in that turn, even if unrelated conversation or work follows before the final response. `pursuit-stop` discards the provisional timer automatically — authoritative timing wins.
7. **Report exactly once** using the values returned by `pursuit-stop` (precise timing) or `provisional-commit` (disclosed fallback), and the preserved statement shape.

Do not leave a pursuit or provisional timer open while waiting for the user. Commentary about the active work remains inside the same pursuit; unrelated commentary does not. A later user message begins a new opportunity for pursuit, not automatic timing.

### Provisional fallback

When authoritative pursuit timing succeeds, the provisional timer is silently discarded by `pursuit-stop`. When no North Star work occurs in a turn, call `provisional-discard` before responding — this removes the timer without creating a ledger row or timing statement.

When North Star work occurred but the precise authoritative timer was genuinely missed, call `provisional-commit` to create exactly one disclosed full-turn fallback row. The response must disclose that full-turn fallback scoping was used. Never invent intermediate timestamps, backdate a helper command, or guess a narrower interval.

Never count both intervals for the same turn. The provisional timer must not remain open across a normal response handoff.

### Mandatory pre-response completeness check

Before every response while a North Star is active and unpaused, verify:

1. If North Star work was pursued this turn, either `pursuit-stop` succeeded (authoritative row recorded) or `provisional-commit` succeeded (fallback row recorded and disclosed). Never both.
2. If no North Star work occurred, the provisional timer was discarded via `provisional-discard` and no ledger entry was manufactured.
3. No provisional or authoritative timing state remains open.
4. If this is a Full Mode run, verify whether every Prompt Contract DoD item has evidence, Format and Constraints are verified, no Failure condition is active, and no user review gate remains. If so, `finalize-north-star` was invoked or is being invoked in this response. A Full Mode run that is contract-complete but unfinalized at response time is a failure.

Do not mark a criterion complete because time was spent or an action was attempted. Record evidence first.

When work drifts away from the North Star — unrelated debugging, a tangent, or an extended discussion that does not advance the objective — stop the current pursuit before the drift and offer to formally pause the run. Never invoke `pause` unilaterally. Formal pause is for intentional suspension across future turns; it is not routine pursuit closure.
## Refine A Live Run

When the user materially changes GOAL, CONSTRAINTS, FORMAT, DEFINITION OF DONE, or FAILURE, call `prompt-contracts` again in embedded caller mode, preserve valid progress, and use the helper's `refine` command. Re-evaluate DoD completion rather than silently carrying marks onto changed criteria. Do not rewrite the contract for evidence-only checkpoints.

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" refine \
  --artifact "<live-path>" \
  --acting-agent "<truthful agent family>" \
  --goal "<refined goal>" \
  --constraint "<current constraint>" \
  --format "<current required format>" \
  --definition-of-done "<current required check>" \
  --failure "<current failure condition>" \
  --verify-complete 1 \
  --batch "<current batch>" \
  --next-action "<next action>" \
  --note "<reason for refinement>"
```

## Progress Communication

Keep the user informed before major actions, after important findings, when the approach changes, and during long tool work. Commentary updates remain within the current pursuit. At a final response or Batch handoff, report completed work, evidence, changed artifacts, unresolved risks, and the exact continuation point.

If the turn pursued the North Star, close its pursuit first and report the helper-provided latest pursuit duration and grand total exactly once. Never compute either value from timestamps.
## Active Pursuit Time Reporting

Active pursuit time is a ledger of discrete, correctly scoped North Star work segments. There is no inactivity threshold, grace period, automatic exclusion, or guessed pause. `pursuit-start` fires when North Star work actually begins in a turn, and `pursuit-stop` fires when that work actually ends. Unrelated work in the same turn stays outside the segment.

Each completed ledger row records:

- a sequential pursuit number;
- batch label;
- one-line work summary;
- helper-captured start and end timestamps for audit; and
- helper-computed duration.

The helper computes the grand total as the sum of completed pursuits. Agents must never calculate durations or totals from timestamps. `status --json` provides `latest_pursuit`, `grand_total_seconds`, and `grand_total_time`; backward-compatible `active_pursuit_seconds_current` and `active_pursuit_time_current` contain the same grand total.

### Reporting contract

For every response from a turn that pursued the North Star, report exactly one timing statement using the production formatter:

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" format-receipt \
  --artifact "<live-path>" --type timing-statement
```

The formatter outputs the unchanged contract shape: `Pursuit <N>: <duration> — <summary>. Grand total: <duration>.`

For fallback pursuits, also emit the disclosure:

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" format-receipt \
  --artifact "<live-path>" --type fallback-disclosure
```

The formatter refuses to produce response text while `active_pursuit` or `provisional` timing remains open. Agents must use the formatter rather than independently composing equivalent wording. Never compute a duration or total from timestamps. If a turn performed no North Star pursuit, do not manufacture a ledger entry or timing statement. The star footer remains compulsory because footer presence follows active lifecycle, not whether that turn contained pursuit.

For Full Mode same-pass finalization, `finalize-north-star` owns the one timing statement in its completion receipt. Do not print a separate pre-finalization statement. For Batch or deferred work, stop and report the pursuit while the artifact remains `IN PROGRESS`.

### Incomplete North Star Response — Failure Conditions

A North Star response is incomplete when any of these conditions is true:

1. The timing statement is absent on a turn that pursued the North Star.
2. A duration or total was computed, inferred, backdated, or guessed instead of read from the helper-derived values returned by `pursuit-stop` or `provisional-commit`. A finalizer may re-read those same frozen values from helper state but must never recompute them.
3. More than one North Star timing statement appears in the response.
4. A ledger entry or timing statement was manufactured for a turn that performed no North Star pursuit.
5. `pursuit-start` was never called on a turn that did pursue the North Star (authoritative), or `provisional-commit` was never called after genuine pursuit with a missed precise timer (fallback). One of these two helper commands must produce the timing values for every pursued turn.
6. A provisional fallback pursuit was committed without explicit disclosure that full-turn fallback scoping was used.
7. Both an authoritative pursuit row and a provisional fallback row were recorded for the same turn.
8. An open provisional timer or authoritative pursuit remains unclosed before the response is sent.
9. The selected-star footer is absent, incorrect, duplicated, or not the final line on any applicable response, including Full, Batch, Paused, refused, deferred, and successful-finalization responses.
10. A Full Mode run with every Prompt Contract completion gate met and no user review gate remaining was left `IN PROGRESS` at response time instead of being finalized through `finalize-north-star`.

Do not send an incomplete response. Correct the helper lifecycle, reporting, and footer before yielding control to the user.

### Explicit pause and interruption recovery

Routine pursuit closure is not `pause`. Explicit `pause` and `resume` remain for a user-approved suspension across turns, and the paused footer remains visible every turn. Neither command creates timing automatically.

If a turn is interrupted while a pursuit is open, `recover` discards the open segment and records an auditable correction; it never guesses an end time or counts the segment. Start a fresh pursuit when North Star work resumes.

### Corrections and reopening

Use `pursuit-remove --number <N> --reason <reason>` only when a ledger entry is known to be wrong. The helper removes it, renumbers later pursuits, and appends the removed entry and reason to `pursuit_corrections`. Never silently edit a duration.

Reopening a terminal artifact preserves its completed pursuits and correction history. The next pursued segment receives the next sequential number, and the grand total continues from the preserved ledger.
## Accountability

For every checklist item:

- identify the check before claiming completion;
- collect current-session, durable, test, inspection, or user-confirmed evidence;
- verify constraints and boundaries too;
- leave unsupported items unchecked; and
- recheck uncertain or interrupted work.

Before closure, review the full objective and checklist. If anything lacks evidence, continue or report the exact blocker.

## Checkpoint, Pause, Resume, Recover, And Status

Use the helper commands documented in `references/state-helper.md`:

- `provisional-start` opens the per-turn safety-net timer (idempotent);
- `pursuit-start` opens the precisely scoped North Star work segment;
- `pursuit-stop` closes it, appends one ledger row, and discards the provisional timer;
- `provisional-discard` removes the provisional timer without a ledger row;
- `provisional-commit` creates one disclosed full-turn fallback row;
- `checkpoint` records batch, next action, notes, completed DoD checks, active Failure conditions, and known-iteration mode transitions without changing timing;
- `pause` and `resume` preserve deliberate user-approved suspension and refuse open provisional or authoritative timing;
- `recover` discards an interrupted open pursuit and any open provisional timer without counting guessed time;
- `pursuit-remove` makes an auditable correction and sequentially renumbers;
- `feedback-add --descriptor "<short label>" --body "<message>"` appends one numbered `### Feedback N` subsection to the Feedback Section, stamped with the acting agent, its model, and a clock-read timestamp. This is the cross-agent channel: an orchestrator, a verifier, and an implementer all write here, and each reads what the others left;
- `reopen` returns a terminal artifact to Live with its ledger intact;
- `status --json` reports the latest pursuit, provisional state, and helper-computed grand total;
- `format-receipt --type <kind>` outputs the exact production user-facing text for timing statements, fallback disclosure, Prompt Contract opt-in display, all selected-star footer states, and finalizer receipts — agents must use this rather than independently composing equivalent wording; and
- `end` archives an explicitly abandoned run without pretending it succeeded.

After interruption, inspect actual workspace state and reverify uncertain work. Never blindly repeat destructive or non-idempotent actions.
## Deliberate Finalization

When every Prompt Contract completion gate has evidence:

- In a Full Mode, fully authorized pass, invoke `finalize-north-star` immediately when that skill is available and no user review gate remains. This is the **same-turn finalization** case: per **Active Pursuit Time Reporting**, the final active pursuit time is reported exactly once, in the final completion receipt — do not also emit a pre-finalization timing line in the same response.
- In Batch Mode, or when the user requested a review before closure, leave the artifact `IN PROGRESS` and hand off the exact finalization command. This is the **objective-met, finalization deferred** case: report the current cumulative active pursuit time in the ready-to-finalize handoff now, and let `finalize-north-star` report the final duration later in its receipt.
- If completion evidence is ambiguous, do not invoke the finalizer.
- If `finalize-north-star` is unavailable, leave the artifact live and tell the user to install or load it. Never finalize or move the file manually.

`finalize-north-star` verifies GOAL, every DoD item, CONSTRAINTS, FORMAT, and FAILURE review from evidence, marks only supported DoD items complete, changes the lifecycle to `FINALIZED`, and moves the file to the matching Historical subject folder without changing its number. It owns the final completion receipt and successful-finalization footer.

## Lifecycle

- **IN PROGRESS** — actively pursued or waiting at a Batch handoff.
- **PAUSED** — intentionally inactive; indicator and timing are preserved.
- **FINALIZED** — verified and closed through `finalize-north-star`.
- **ENDED** — explicitly abandoned without claiming success and archived as `_ended.md` under the matching Historical Subject.

A blocker pauses or leaves the run in progress; it does not prove completion.

## Feedback Section

Every North Star artifact carries a `## Feedback Section`, **present and empty by default**, rendered immediately above `## Agent Change Log` and therefore above the terminal Base64 state.

It exists so agents can talk to each other through the artifact instead of through a chat session neither of them shares. An orchestrator writes what it needs verified; a verifier writes what it found; the implementer writes back what it changed. Each reads what the others left, across platforms and across sessions.

**This section is helper-owned, which makes it different from every other skill's Feedback Section.** It lives in the encoded state, so a hand-written entry is silently discarded by the next helper mutation. Append only through:

```text
python -X utf8 "<skill-dir>/scripts/north_star_state.py" feedback-add \
  --artifact "<live-path>" \
  --acting-agent "<truthful agent family>" \
  --acting-llm "<truthful model name>" \
  --descriptor "<short label>" \
  --body "<the message>"
```

The helper numbers each entry `### Feedback N — <clock timestamp> — <agent> — <descriptor>`, starting at 1 and never renumbering. Entries are append-only and immutable: a correction is a **new** entry, never an edit to an earlier one. An empty Feedback Section is correct and must never be pruned for being empty — `finalize-north-star` preserves it as found.

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to North Star artifacts and every checkpoint, refinement, pause, resume, recovery, end, or lifecycle update.

For every in-scope artifact:

- always create exactly one `## Agent Provenance` section immediately after the `North Star lifecycle:` line, before Subject, Topic, and the remaining North Star content;
- render Agent Provenance only as the canonical two-column `Field | Value` table with `Content owner`, `Original writing agent`, `Original writing LLM`, `Created`, and `Artifact role` rows, in that order;
- use a stable truthful agent-family label such as `Codex Agent`, `Claude Agent`, `Antigravity Agent`, `Hermes Agent`, or `zCode Agent`, and pass the model separately through `--writing-llm`;
- keep the original writing-agent entry immutable; `Original writing LLM` is likewise immutable once recorded, and `refine --writing-llm` may set it only while it still reads `Not recorded`;
- always create exactly one append-only `## Agent Change Log`, store it in helper-owned state, and render it as the final human-readable section immediately before `north-star:state-b64`, as a five-column `Date and Time | Agent | Model | Action | Scope` table with `YYYY-MM-DD-HH:mm:ss` timestamps read from the machine clock;
- always create exactly one `## Feedback Section` immediately above the change log; it is helper-owned state, empty by default, and appended to only through `feedback-add`, which numbers each entry `### Feedback N — date — agent — descriptor`;
- never hand-edit the Feedback Section. Because it lives in helper-owned Base64 state, a hand-written entry is silently discarded by the next helper mutation. Any agent, on any platform, appends through `feedback-add`;
- pass truthful `--acting-agent "<agent family>"` on every material helper mutation; the helper refuses material changes that cannot be attributed;
- if a legacy artifact lacks reliable creator evidence, use `Not recorded` rather than guessing, then log the current agent's actual change; and
- treat copying or global synchronization as transport, not authorship.

Keep `Content owner` for now. In Uzo's personal artifacts it normally resolves to `Uzo`; do not confuse content ownership with the agent that performed the filesystem write. Do not inject provenance into product source, third-party files, databases, generated caches, skill definitions, schema-sensitive or machine-consumed files, or other operational files unless their schema explicitly supports it.

## Durable Artifact Format Handling

This skill owns the North Star objective, checklist, permanent number, encoded state, timing, checkpointing, location, and lifecycle. When co-invoked with `html-this` or `pdf-this`, create only the requested durable format unless the user requests multiple formats. Use a temporary native state representation only as needed by `north_star_state.py`, then embed it through the format skill and leave no durable Markdown intermediate.

On checkpoint, refine, pause, resume, recover, reopen, or end, recover the embedded native source when necessary, apply the helper operation, and regenerate every existing same-stem format sibling as one atomic artifact set. Deduplicate siblings during number scans. This section overrides `.md`-only examples only for co-invoked serialization; every encoded-state and lifecycle gate remains mandatory.

## Exact Model Attribution

Whenever this skill writes a new model identity, appends a current-run model value, or defines a workflow that does either:

- Record the full model identity actually used when it is safely available from current runtime or session metadata. Use a specific identity such as `GPT-5.6 Sol`, `GPT-5.6 Terra`, or `Claude Opus 5`; a family-only label such as `GPT-5`, `Claude`, or `Codex Agent` is not an acceptable substitute.
- Resolve identity in this order: current runtime or session metadata; a platform-provided current-model field; only then, when unavoidable, a field-minimized configuration lookup that returns the model field alone. Apply `tread-lightly` to any potentially sensitive configuration and never display, copy, search, diff, or log the whole configuration.
- Keep the agent family and model identity separate. Never infer an exact model from an agent label, provider name, stale configuration, or model family.
- Use `Not recorded` only when the exact identity genuinely cannot be established safely. Do not replace an available exact identity with `Not recorded` merely to avoid checking current runtime metadata.
- Preserve append-only history. Never rewrite a historical provenance or change-log value solely to improve an old model label; add a truthful current correction entry when correction is required.

**Validation check:** For every model value newly written in the current run, accept a full exact identity and the honest `Not recorded` fallback, but reject known ambiguous family-only labels or agent-family substitutions. Confirm model discovery exposed only the required model field and that no historical row was rewritten.

## Validation

When creating or updating this skill:

- validate with `quick_validate.py` in Python UTF-8 mode;
- smoke-test creation under Live with combined Live/Historical numbering;
- smoke-test stable indicator reuse, refinement, checkpointing, pause/resume, recovery, status, ending, and a second independent run;
- confirm an unchecked DoD item, active Failure condition, unverified Format or Constraints, and an open pursuit each block finalization;
- smoke-test `finalize-north-star` moving a verified run to Historical;
- confirm helper edits remain inside the chosen artifact and collisions never overwrite; and
- confirm all global copies validate and have recursive byte parity.
- confirm provenance immediately follows lifecycle, uses the Field/Value table with all five canonical rows in order including `Original writing LLM`, and remains above every other North Star section;
- confirm the Feedback Section exists exactly once, sits immediately above the change log, renders numbered `### Feedback N` subsections, and accepts entries from any acting agent through `feedback-add`;
- confirm the Agent Change Log renders the five columns `Date and Time`, `Agent`, `Model`, `Action`, `Scope`, that new rows carry clock-read `YYYY-MM-DD-HH:mm:ss` timestamps, and that pre-migration date-only rows keep `Not recorded` in `Model` rather than being backfilled;
- confirm a legacy schema-6 artifact migrates in place on its next mutation without losing pursuits, corrections, or terminal state;
- confirm Agent Change Log is the final human-readable section, Base64 state is last, and material mutations without `--acting-agent` are refused without changing the file.

When updating pursuit timing, reporting, or footer enforcement, additionally prove all of the following:

- the named **Incomplete North Star Response — Failure Conditions** block exists and states all required timing failures: missing pursued-turn statement, computed rather than helper-derived duration, duplicate timing statements, manufactured no-pursuit entry, and missing `pursuit-start` or `provisional-commit`;
- footer omission is also an explicit failure;
- the selected-star footer is compulsory for Full, Batch, Paused, refused, deferred, and successful-finalization responses, including turns with no pursuit;
- `pursuit-start` occurs when North Star work actually begins and `pursuit-stop` when it actually ends;
- unrelated same-turn work is excluded from the pursuit;
- imprecise scoping uses and discloses the full-turn fallback without guessed timestamps;
- every pursued response uses exactly one unchanged-shape timing statement sourced from the helper via `pursuit-stop` (precise) or `provisional-commit` (fallback), and a no-pursuit turn manufactures none;
- waiting between pursuits never changes the grand total;
- Full Mode same-pass finalization reports latest pursuit and grand total exactly once through `finalize-north-star`;
- explicit pause/resume remains user-approved and independent of pursuit closure;
- recovery discards an interrupted open pursuit without guessing duration;
- removing an incorrect pursuit records the removed entry and reason, then renumbers the remaining ledger sequentially; and
- reopening preserves all prior pursuits, enters Batch Mode, and begins with the next number;
- pursuit 2 cannot begin while current mode remains Full, and a known iteration can transition immediately after pursuit 1;
- material contract refinement updates the embedded contract while evidence-only checkpoints do not churn it;
- Prompt Contract display remains opt-in and never becomes an approval gate; and
- the Base64 state marker followed by `north-star:run-end` remains the final nonblank content after every lifecycle mutation.
