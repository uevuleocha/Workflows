---
name: finalize-north-star
description: Finalize an in-progress North Star after verifying its full Prompt Contract from evidence, change its lifecycle to FINALIZED, preserve its number and subject, and move it from Archive Live to Archive Historical while reporting the selected-star finalized-turn footer. Use when the user invokes finalize-north-star or asks to close, complete, or finalize a North Star.
---

# Finalize North Star

Close a verified North Star deliberately. This is the only workflow that may change a North Star from `IN PROGRESS` to `FINALIZED` or move it from `Archive/Live/North Stars/` to `Archive/Historical/North Stars/`.

## Project Contract

Obey the active workspace contract, permissions, safety rules, and UTF-8 requirements. Finalization does not broaden the authorized task.

## Invocation

Treat these as direct invocation:

- `/finalize-north-star`
- `$finalize-north-star`
- `use finalize-north-star`
- `use the finalize-north-star skill`
- `finalize the North Star`
- clear equivalents that ask to close a live North Star

If the user asks to start, revise, continue, or resume a North Star, use `north-star` instead.

## Required Dependency

This skill requires `north-star`, including `scripts/north_star_state.py`, and the embedded Prompt Contract authored through `prompt-contracts`. The helper owns encoded lifecycle state, contract gates, status rewrite, suffix rename, terminal machine-state placement, and the collision-safe move.

This skill inherits `north-star`'s compulsory selected-star footer, precise pursuit-start/pursuit-stop scoping, helper-only timing authority, exactly-once timing rule, and incomplete-response failure contract. Finalization narrows those rules for lifecycle closure; it does not replace or weaken them.

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
4. the full Prompt Contract, DoD completion state, active Failure state, evidence, mode transitions, checkpoint notes, and next action; and
5. referenced deliverables or validation output needed to prove completion.

Do not expand into a broad workspace audit.

## Pursuit Ownership And Scoping

Apply exactly one of these branches:

- **Standalone substantive finalization:** when this skill performs review or verification that advances the North Star, call `provisional-start` at turn open. When precise scoping is possible, call `pursuit-start` at the actual beginning of that work and `pursuit-stop` at its actual end. When precise scoping was genuinely missed, call `provisional-commit` to create one disclosed full-turn fallback row. Keep unrelated same-turn work outside the pursuit interval in either case.
- **Same-pass finalization:** when the parent North Star workflow already stopped the pursuit at the actual end of its work, use that closed pursuit. The parent's `pursuit-stop` already discarded the provisional timer. Do not start or stop a duplicate pursuit for finalization mechanics or its receipt.
- **No pursued work:** when this skill only checks existing helper state and performs lifecycle closure, discard the provisional timer with `provisional-discard` and do not manufacture a ledger entry.

No branch may leave an open provisional timer before finalization. If precise scoping is genuinely impossible, use the disclosed provisional fallback rather than guessing. The helper remains the only timing source in every branch; never calculate duration from timestamps.

## Target Selection

Use the live North Star the user explicitly references.

Otherwise scan `Archive/Live/North Stars/` recursively for `*_in_progress.md`:

- if exactly one exists, use it;
- if exactly one clearly matches the active GOAL, use it;
- if several are plausible, ask which one to finalize;
- if none exists, report that there is no in-progress North Star.

Never finalize a file already under `Archive/Historical/North Stars/`.

## Completion Gates

Finalization is evidence-based. Before closing:

1. Run the helper's `status --json` command.
2. Confirm the selected run is `in_progress` or `paused`.
3. Confirm the Prompt Contract GOAL is reached.
4. Verify every in-pass DEFINITION OF DONE item from direct user confirmation, current-session evidence, or durable recorded evidence. Mark an unchecked in-pass item complete only when that evidence supports it; never tick unsupported work. Preserve `## Deferred Real-World Verification` items without treating them as closure gates.
5. Confirm every CONSTRAINT was respected and every required FORMAT deliverable exists in the required shape.
6. Review every FAILURE condition and confirm none is active. A bad result means at least one Failure condition occurred; it cannot be finalized.
7. Confirm any substantive standalone pursuit was closed with `pursuit-stop` (precise) or `provisional-commit` (disclosed fallback), or that same-pass finalization is using the parent's already-closed pursuit; in every case, confirm `active_pursuit` is `null` and `provisional` is `null`, and no duplicate or manufactured pursuit was added.

Existence, age, or a nearly complete contract is not completion evidence. Never invent evidence, silently check unsupported DoD criteria, clear a real Failure condition, or extend pursuit timing through finalization work.

If any required item is incomplete, ambiguous, blocked, or unsupported, leave the file `IN PROGRESS` and ask for the missing evidence or an explicit, recorded deferral. A deferral is valid only when the remaining work no longer belongs to this North Star.

Before a refused or deferred response, stop any standalone pursuit this finalizer opened and report that helper-derived pursuit statement exactly once. Leave the artifact active or paused. Use `format-receipt --type mode-footer` so the selected-star Full, Batch, or Paused footer remains the true final line. Successful finalization also requires the selected-star `FINALIZED THIS TURN` footer on that response; it disappears only on later unrelated responses.

## Finalization

For standalone substantive finalization, close the pursuit at the actual end of review and verification:

```text
python -X utf8 "<north-star-dir>/scripts/north_star_state.py" pursuit-stop \
  --artifact "<live-north-star-path>" \
  --acting-agent "<truthful agent family>" \
  --batch "<batch label>" \
  --summary "<one-line work actually completed>"
```

For same-pass finalization, do not run this command again when the parent pursuit is already closed. For a no-pursuit finalizer, do not run it at all. After every gate passes and helper state confirms no open pursuit, run:

```text
python -X utf8 "<north-star-dir>/scripts/north_star_state.py" finalize \
  --artifact "<live-north-star-path>" \
  --acting-agent "<truthful agent family>" \
  --evidence "<final verification evidence>" \
  --verify-complete <evidence-supported DoD number> \
  --constraints-verified \
  --format-verified \
  --failure-reviewed \
  --note "Finalized through finalize-north-star."
```

The helper must:

- refuse finalization while timing is open, an in-pass DoD item is unchecked, a Failure condition is active, or Constraints, Format, or Failure review is unverified; an unticked `## Deferred Real-World Verification` item is not a refusal condition;
- change the run status and visible header to `FINALIZED`;
- preserve the Subject, Topic, complete `N.)` prefix, ledger, and corrections;
- rename only `_in_progress.md` to `_finalized.md`;
- move the file from Live to the matching Historical Subject;
- refuse to overwrite or renumber on collision; and
- leave no duplicate on the Live side.
- preserve exactly one mandatory Agent Provenance table immediately after lifecycle, with all five canonical rows including `Original writing LLM`, and append the finalizer entry to the helper-owned five-column Agent Change Log;
- preserve exactly one Feedback Section immediately above the change log, including an empty one;
- refuse unattributed finalization when `--acting-agent` is absent; and
- keep Agent Change Log as the final human-readable section immediately before terminal Base64 state.

Finalization does not add timing. Read `latest_pursuit`, `grand_total_seconds`, and `grand_total_time` from helper state after the move. These are authoritative; never compute a duration or total from timestamps. Use the current local date in the finalized presentation.
## Mandatory Completion Receipt

Every successful finalization must use the production formatter:

```text
python -X utf8 "<north-star-dir>/scripts/north_star_state.py" format-receipt \
  --artifact "<finalized-historical-path>" \
  --type finalizer-receipt \
  --subject "<Subject>"
```

The formatter outputs the exact populated statement and a clickable Markdown artifact link. It refuses to produce output while `active_pursuit` or `provisional` timing remains open. Agents must use the formatter rather than independently composing equivalent wording.

After the receipt, call the formatter again with `--type mode-footer` against the finalized Historical path and use its `Mode = <selected-star> North Star (FINALIZED THIS TURN)` output exactly once as the true final response line.

- `<N>` is the permanent North Star number.
- `<P>`, pursuit duration, and summary come from `latest_pursuit` after the final pursuit was closed. The helper-derived `latest_pursuit` may come from `pursuit-stop` (precise authoritative timing) or `provisional-commit` (disclosed full-turn fallback). Exactly-once reporting and helper-only arithmetic remain compulsory in both cases.
- `<grand-total>` comes from `grand_total_time` after finalization.
- `<artifact link>` points to the finalized Historical artifact.

If the artifact has only one pursuit, latest and grand total may be equal; both labels remain explicit. If no completed pursuit exists, finalization is incomplete because there is no pursued evidence-bearing turn to report.

### Pre-response completeness check

For successful finalization, confirm all of the following before replying:

1. any substantive pursued work was closed through `pursuit-stop` (precise) or `provisional-commit` (disclosed fallback), while same-pass or no-pursuit closure added no duplicate or manufactured entry;
2. no provisional timer or authoritative pursuit remains open;
3. `finalize` succeeded and the Live source is absent;
4. latest pursuit and grand total came from helper output, not inference;
5. the populated statement appears exactly once; and
6. no separate pre-finalization timing line duplicates it.
7. the Prompt Contract review is recorded in helper state and every completed DoD item has evidence; and
8. the selected-star `FINALIZED THIS TURN` footer appears exactly once as the true final line.

For refused or deferred finalization, confirm all of the following before replying:

1. any pursuit opened by this finalizer was stopped and reported once, and any provisional timer was discarded;
2. no duration was calculated from timestamps and no duplicate or manufactured ledger entry was added;
3. the artifact remains `IN PROGRESS` or `PAUSED`; and
4. the selected Full, Batch, or Paused star footer is the final line of the response.

A response is incomplete if pursued work lacks both `pursuit-start` (precise) and `provisional-commit` (fallback), if timing remains open, if an entry is manufactured, if timing is agent-computed or duplicated, if the Prompt Contract was not fully reviewed from evidence, or if the applicable selected-star footer is missing—including on successful closure.

A Full Mode run completed in the current pass must be finalized in that same pass when authority and evidence permit. Finalization itself does not extend timing.
## No Manual Fallback

Only this skill, through the North Star helper, may finalize and move a North Star. If the helper cannot complete the guarded operation, stop and report the exact failure. Do not hand-edit the status, rename the suffix, or move the file as a substitute.

## Output

Report:

- the original Live path;
- the final Historical path;
- the Prompt Contract evidence used for GOAL, DoD, CONSTRAINTS, FORMAT, and FAILURE review;
- any explicit deferrals;
- confirmation that the Live source no longer exists; and
- the exact mandatory receipt containing latest pursuit and grand total.

The timing statement appears exactly once, inside the receipt, sourced from helper state. Do not emit a second duration line. Do not paste the Prompt Contract unless the user opted in or asks to see it.

When finalization is refused or deferred, report the missing gate, any helper-derived pursuit statement required by this turn, and the next action. Keep the selected Full, Batch, or Paused star footer as the final line. Do not emit the successful-finalization receipt.

## Agent Provenance For Durable Artifacts

Finalization never replaces the original creator. Preserve exactly one `## Agent Provenance` section immediately after the lifecycle line, including its canonical two-column `Field | Value` table and its immutable `Original writing agent` and `Original writing LLM` rows. Pass the truthful finalizer through required `--acting-agent`, and its model through `--acting-llm`; the helper appends the lifecycle action to its state-owned `## Agent Change Log` as a five-column `Date and Time | Agent | Model | Action | Scope` row with a clock-read `YYYY-MM-DD-HH:mm:ss` timestamp. That log is compulsory and must remain the final human-readable section immediately before the Base64 marker. Preserve exactly one `## Feedback Section` immediately above it, including an empty one — never prune a Feedback Section because it carries no entries, and never tick or rewrite what an earlier agent left there. The Base64 state marker and `north-star:run-end` remain the final two nonblank lines with nothing below them.

**Publication steps are never a closure gate.** A wiki sync, a `stage-commit-push` run, a GitHub push, or a submodule pointer bump must never block, defer, or fail finalization, and this finalizer never performs one itself. Those operations belong after the artifact reaches its final Historical path — finalization renames and moves the file, so syncing first leaves the wiki holding a synthesised copy of a path that no longer exists. Where such an item appears in a DEFINITION OF DONE or Verification Checklist, report it, recommend a waiver, and close.

When same-stem Markdown, HTML, or PDF siblings exist, apply the same provenance history to the complete artifact set. If a legacy artifact lacks reliable creator evidence, record `Original writing agent: Not recorded` rather than guessing, and log the current finalizer's work. Do not add embedded provenance to product source, third-party files, databases, generated caches, skill definitions, schema-sensitive or machine-consumed files, or other operational files unless their schema explicitly supports it.

## Durable Artifact Format Handling

This skill still owns every Prompt Contract, evidence record, and finalization gate. Before finalizing, discover same-stem `.md`, `.html`, and `.pdf` siblings and treat them as one North Star artifact set. Recover embedded native state when the helper needs it, preflight every destination, apply final state, rename the lifecycle suffix on every sibling, and move the complete set together.

An HTML-only or PDF-only North Star remains in that format; do not manufacture Markdown. Stop rather than finalize only part of a sibling set. Extension-only search and helper-path examples become format-neutral for this run.

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

When creating or updating this skill:

- validate it with `quick_validate.py` in Python UTF-8 mode;
- smoke-test successful finalization of a fully verified North Star;
- confirm an unchecked in-pass DoD item, active Failure condition, and unverified Constraints or Format each block finalization, while an unticked `## Deferred Real-World Verification` item does not;
- confirm the number, Topic, Subject, indicator, timing, and evidence survive;
- confirm a Historical collision blocks without overwriting;
- confirm the Live source disappears only after a successful move; and
- confirm all global copies validate and have recursive byte parity.

Also prove each finalizer ownership branch:

- standalone substantive review starts and stops one precisely scoped pursuit;
- same-pass handoff consumes the parent's already-closed pursuit without a duplicate;
- a no-pursuit finalizer manufactures no ledger row;
- refused or deferred finalization closes and reports any pursuit it opened, preserves active or paused state, and retains the selected Full, Batch, or Paused star footer;
- precise scoping excludes unrelated same-turn work; and
- the full-turn fallback is used only when needed and is explicitly disclosed.

When updating the **Mandatory Completion Receipt** contract, additionally prove:

- finalization refuses an open pursuit;
- the pursuing turn is closed before finalization and excludes user waiting and finalization-reporting time;
- the receipt contains latest pursuit number, helper duration, one-line summary, and helper grand total exactly once;
- reopening, another pursuit, and re-finalization preserve earlier rows and report the new latest pursuit plus accumulated total;
- omission, timestamp arithmetic, stale values, or duplicate timing makes the response incomplete;
- the successful finalization response ends with the selected-star `FINALIZED THIS TURN` footer exactly once;
- Prompt Contract display remains opt-in rather than automatic; and
- the Agent Change Log remains the final human-readable section immediately before Base64 state while `north-star:run-end` remains terminal.
- provenance remains immediately after lifecycle in the canonical five-row Field/Value table, the Feedback Section survives finalization even when empty, Agent Change Log is the final human-readable section with its five columns intact, and missing `--acting-agent` blocks finalization without mutation;
- an unperformed wiki sync, push, or submodule pointer bump never blocks or defers finalization, and the finalizer performs none of them.
