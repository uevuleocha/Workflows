---
name: finalize-report
description: Finalize an existing pending report after verifying completion evidence, update its dismissible footer to REPORTED, rename its suffix, move it from Live Reports to Historical Reports while preserving its permanent number, and delete the report's send-ready staged copies. Use when the user asks to finalize, close, mark reported, sent, or read a pending report.
---

# Finalize Report

Close an existing pending report as `reported`. This skill never creates, updates, or reopens a report; route those requests to `report-this`.

```text
From: <root>\Archive\Live\Reports\<Subject>\N.) <Topic>_pending.md
To:   <root>\Archive\Historical\Reports\<Subject>\N.) <Topic>_reported.md
```

Terminal state is always `reported`, regardless of report mode and regardless of whether the user sent the report externally or read/accepted it personally.

## Project Contract

Follow the workspace's canonical contract. Preserve UTF-8, user data, approval gates, and public-repository safety rules.

## Invocation

Treat these as direct invocation:

- `/finalize-report` or `use finalize-report`
- `finalize report`, `close this report`, or `mark this report reported`
- direct confirmation such as `I've sent it` or `I've read it, close it` when a pending report is clearly referenced

Requests to create, revise, extend, or reopen route to `report-this`.

## Target Selection

Use the user-referenced pending report. Otherwise scan recursively under `Archive\Live\Reports\` for `_pending.md` files. Use the sole clear match; ask when multiple reports are plausible; stop when none exists.

Never finalize a report already under Historical or one ending `_reported.md`. Reopening belongs to `report-this`.

## Completion Evidence

Do not rubber-stamp. Finalize only with at least one valid evidence route:

- direct user confirmation that the report was sent, read, accepted, or should be closed
- current-session or durable evidence that its stated purpose is complete
- satisfaction of an embedded Prompt Contract, when one exists

If the report contains a Prompt Contract, review each DEFINITION OF DONE item and every FAILURE condition. Every in-pass DoD item must be satisfied or explicitly waived by the user, and no unwaived FAILURE condition may remain active. Genuine later-use evidence belongs under `## Deferred Real-World Verification` and never blocks closure.

If evidence is partial or ambiguous, stop and ask. A report's age, existence, polish, or location is not completion evidence.

## Finalization Procedure

1. Read the pending report and preserve its full body and created date.
2. Count canonical dismissible footers. Require exactly one. If the footer is missing or duplicated, stop before changing lifecycle state, suffix, path, or content; route footer repair through `report-this`.
3. Record the original Live path and derive the Historical path using the same unnumbered Subject, permanent `N.)` prefix, and title; change only `_pending.md` to `_reported.md`.
4. Create the matching Historical Subject folder when allowed.
5. Stop if the target filename exists or if its number collides with another Historical report. Never overwrite, delete, or renumber.
6. Replace only the one canonical dismissible footer lifecycle line with: `**Report lifecycle:** REPORTED ✅ — created <date>, reported <today>.` Keep the footer fencing and delete-before-sending instruction intact. Do not add a mode tag or top lifecycle header.
7. Move the file Live to Historical as a true move. Leave no duplicate in Live.
8. Verify the final path, suffix, footer, number, Subject, body preservation, absence of the Live source, and UTF-8.

## Staged-Copy Cleanup

Finalizing a report normally means it has been sent, so its send-ready copy has served its purpose. For each report finalized in a pass, after the pending-to-reported transition succeeds, look for a staged copy at the staging path its Subject implies and delete that copy if present. Absence is not an error; many reports are finalized without ever being staged.

The staging path is the one `report-this` uses: `<workspace root>\tmp\<Subject>-reports-send-ready\`, where the Subject segment is the report's own Subject folder name, lowercased and hyphenated where it contains spaces. The staged copy name preserves the permanent `N.)` prefix and the Topic, with the `_pending` suffix dropped.

Then apply the folder rule. After deleting staged copies in a pass, if the staging folder for that Subject now contains no files, delete the empty folder as well. If it still contains staged copies for reports not finalized in this pass, leave it in place. This must behave correctly across passes: three reports staged, two finalized together, then the third finalized later, must leave no folder behind after the final pass. A later staging request simply recreates the folder under the same name.

Safety boundaries are strict:

- never delete anything outside the Subject's own staging folder;
- never delete a file in the staging folder that does not correspond to a report finalized in this pass;
- never delete a non-empty folder;
- if the staging folder contains unexpected files the workflow did not create, leave them and the folder alone and say so rather than removing them.

Report the cleanup outcome as part of the finalization report: which staged copies were deleted, which were absent, and whether the staging folder was removed or retained and why.

Ownership stays clean: `finalize-report` owns cleanup (deleting copies attributable to reports it just finalized, and removing the folder when it empties). `report-this` owns staging (which reports, the folder name, the strip list, and verification). Neither skill takes on the other's job, and cleanup never becomes a side effect of staging or vice versa.

## File And Number Rules

- Subject folders are never numbered.
- Preserve the `N.)` number for life. Never renumber or reclaim a gap.
- Preserve the report title/body except for the lifecycle suffix and footer lifecycle line.
- Leave an empty Live Subject folder in place; deletion is separate work.
- Touch no unrelated report.

## Output

Report the original Live path, final Historical path, completion evidence, contract outcomes or deferrals, and any unresolved limitation. Do not paste the whole report unless asked.

## Boundaries

Do not create/update/reopen reports, choose a sent/read-specific terminal state, infer completion from existence, overwrite a collision, renumber, remove the dismissible footer, add workflow metadata at the top, send the report, or move a file manually when evidence gates fail. Cleanup deletes only staged copies attributable to reports finalized in this pass: never a foreign file, never a non-empty folder, and never anything outside the Subject's own staging folder.

## Agent Provenance For Durable Artifacts

Finalization never replaces the original creator. Preserve the artifact's `## Agent Provenance` section exactly, including its immutable `Original writing agent` and `Original writing LLM` rows, then append a new entry to its `## Agent Change Log` naming the truthful acting agent, that agent's model, the lifecycle action, and the status/path or content scope changed. The change log is a five-column `Date and Time | Agent | Model | Action | Scope` table; stamp the new row `YYYY-MM-DD-HH:mm:ss` from the machine clock and never estimate it. Leave historical date-only rows exactly as written.

Preserve `## Agent Provenance` immediately after the artifact's opening block -- its title, status, and lifecycle lines -- and keep `## Agent Change Log` as the last section, or immediately above any section the artifact reserves for the last position.

Preserve the artifact's `## Feedback Section` exactly as found, **including an empty one**. Never prune a Feedback Section for carrying no entries, never renumber or rewrite an existing `### Feedback N` subsection, and never author a reply on another agent's behalf. It is an append-only cross-agent record, and finalization is not a reason to tidy it.

**Publication steps are never a closure gate.** A wiki sync, a `stage-commit-push` run, a GitHub push, or a submodule pointer bump must never block, defer, or fail finalization, and this skill never performs one itself. Those operations belong after the artifact reaches its final path -- finalization renames and moves the file, so syncing first leaves the wiki holding a synthesised copy of a path that no longer exists and dirties the repository again immediately. Where such an item appears in a DEFINITION OF DONE or Verification Checklist, report it, recommend a waiver, and close.

**An unticked in-pass box means not done.** Read a blank in-pass checkbox as incomplete, never as "done but awaiting confirmation." Do not supply the executing agent's ticks to make an artifact look finished. Where an in-pass box is unticked but its evidence is plainly present, report the discrepancy to the user rather than silently resolving it in either direction. Unticked items under `## Deferred Real-World Verification` are preserved and reported but never block finalization. Where an invented sync constraint is contradicted by the user's own authorization, report it and recommend a waiver rather than treating it as failure.

When same-stem Markdown, HTML, or PDF siblings exist, apply the same provenance history to the complete artifact set. If a legacy artifact lacks reliable creator evidence, record `Original writing agent: Not recorded` rather than guessing, and log the current finalizer's work. Do not add embedded provenance to product source, third-party files, databases, generated caches, skill definitions, schema-sensitive or machine-consumed files, or other operational files unless their schema explicitly supports it.

## Durable Artifact Format Handling

This skill still owns every evidence, footer, and reporting gate. Before finalizing, discover same-stem `.md`, `.html`, and `.pdf` siblings and treat them as one report artifact set. Preflight every destination, apply reported content/status through the applicable format skill, rename the lifecycle suffix on every sibling, and move the complete set together without changing the permanent prefix or Topic.

HTML-only or PDF-only reports remain in that format; do not manufacture Markdown. Stop rather than finalize only part of a sibling set. Extension-only search and validation examples become format-neutral for this run.

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

Use the aligner's read-only `check` first. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. For safe padding-only findings, run `format` to a distinct nonexistent staged path, review the diff, adopt it, and rerun `check`. Resolve overflow, malformed, or ambiguous findings manually; stop on operational failure. Confirm the dependency is available before the final write, and never silently replace it with raw character counting. The portable rule below remains compulsory.

## Markdown Table Alignment

Every Markdown table this skill writes or causes to be written must be visually pipe-aligned. Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view.

Rendered visual alignment is authoritative; raw `|` indices are diagnostic only, because Unicode display width (emoji, arrows, wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells. When a table exceeds approximately 120 characters in total width, narrow the columns and move detail to notes so it renders on one line without word-wrapping.

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

After finalization, confirm:

- the Live source no longer exists and Historical target exists
- filename ends `_reported.md`
- Subject and permanent `N.)` are unchanged and collision-free
- footer says REPORTED ✅ with created and reported dates
- exactly one canonical dismissible footer exists
- footer retains the delete-before-sending instruction and contains no mode tag
- report body is otherwise unchanged and UTF-8 is preserved

When updating this skill, run `quick_validate.py` with Python `-X utf8` and keep stdout and stderr separate, reading pass/fail from the process exit code. Confirm the `## Markdown Table Alignment` section in this skill remains present in full, and confirm the staged-copy cleanup step, folder rule, and safety boundaries remain in force.
